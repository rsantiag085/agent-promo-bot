import os
import re
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List
from dotenv import load_dotenv
import uvicorn

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from telethon import TelegramClient, events
from sqlalchemy.orm import Session
from src.core.database import SessionLocal, ProductWatch, AlertLog, MonitoredGroup

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    raise RuntimeError("TELEGRAM_API_ID e TELEGRAM_API_HASH são obrigatórios.")

# Regex para Preços e Links
PRICE_REGEX = re.compile(r'R\$\s*\d+(?:[.,]\d+)?', re.IGNORECASE)
URL_REGEX = re.compile(r'(https?://[^\s]+)')

client = TelegramClient('session', int(API_ID), API_HASH)

def extract_metadata(text):
    # Ignorar linhas de cupom e o link subsequente para pegar os dados reais do produto
    lines = text.split('\n')
    cleaned_lines = []
    skip_next_link = False
    
    for line in lines:
        if 'cupom' in line.lower():
            skip_next_link = True
            continue
            
        if skip_next_link:
            if line.strip() == '':
                continue
            if URL_REGEX.search(line):
                skip_next_link = False
                continue
            skip_next_link = False
            
        cleaned_lines.append(line)
        
    cleaned_text = '\n'.join(cleaned_lines)

    prices = PRICE_REGEX.findall(cleaned_text)
    urls = URL_REGEX.findall(cleaned_text)
    
    # Pega o último preço listado (geralmente é o preço com desconto)
    price = prices[-1] if prices else "Preço não detectado"
    link = urls[0] if urls else "Link não detectado"
    return price, link

async def process_message(message, db: Session):
    # Only process if chat is in MonitoredGroup
    monitored_groups = [g.group_username_or_id for g in db.query(MonitoredGroup).all()]
    if not monitored_groups:
        return
    
    text = message.message
    if not text:
        return
    
    try:
        chat = await message.get_chat()
        chat_username = getattr(chat, 'username', None)
        chat_id = str(chat.id)
        
        is_monitored = False
        if chat_username:
            chat_username_with_at = f"@{chat_username}"
            if chat_username in monitored_groups or chat_username_with_at in monitored_groups:
                is_monitored = True
        
        # also check id
        if not is_monitored and chat_id in monitored_groups:
            is_monitored = True
            
        if not is_monitored:
            return
            
    except Exception as e:
        return
        
    watches = db.query(ProductWatch).filter(ProductWatch.is_active == True).all()
    text_lower = text.lower()
    
    for watch in watches:
        keywords = [k.strip() for k in watch.keywords.split(',')]
        if any(kw.lower() in text_lower for kw in keywords):
            price, link = extract_metadata(text)
            
            # Deduplication: avoid same link for same product
            recent_alert = db.query(AlertLog).filter(
                             AlertLog.product_id == watch.id,
                             AlertLog.original_link == link
                           ).first()
                           
            if recent_alert and link != "Link não detectado":
                return
                
            # Log alert
            new_alert = AlertLog(
                product_id=watch.id,
                price_found=price,
                original_link=link,
                group_id=str(chat.id)
            )
            db.add(new_alert)
            db.commit()
            
            # Send Notification
            msg_to_send = f"🚨 **PROMOÇÃO DETECTADA!**\n\n" \
                          f"**Produto monitorado:** {watch.product_name}\n" \
                          f"━━━━━━━━━━━━━━━━━━\n" \
                          f"{text}"
                          
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if bot_token:
                try:
                    import requests
                    me = await client.get_me()
                    # Roda o requests num executor para não travar o loop assíncrono
                    asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            json={"chat_id": me.id, "text": msg_to_send, "parse_mode": "Markdown"}
                        )
                    )
                except Exception:
                    await client.send_message('me', msg_to_send)
            else:
                await client.send_message('me', msg_to_send)
            break # only trigger once per message

@client.on(events.NewMessage)
async def handler(event):
    db: Session = SessionLocal()
    try:
        await process_message(event.message, db)
    finally:
        db.close()

async def fetch_retroactive(product_id: int):
    print(f"Iniciando varredura retroativa para o produto [{product_id}]...")
    db: Session = SessionLocal()
    try:
        watch = db.query(ProductWatch).filter(ProductWatch.id == product_id).first()
        if not watch or not watch.is_active:
            return
            
        monitored_groups = db.query(MonitoredGroup).all()
        for g in monitored_groups:
            try:
                # get chat entity
                entity = await client.get_entity(g.group_username_or_id)
                # fetch last 10 messages
                messages = await client.get_messages(entity, limit=10)
                for msg in messages:
                    # process each message normally
                    await process_message(msg, db)
            except Exception as e:
                print(f"Erro ao buscar retroativo no grupo {g.group_username_or_id}: {e}")
    finally:
        db.close()
    print("Varredura retroativa concluída!")

async def fetch_all_retroactive():
    print("Iniciando varredura retroativa global em todos os grupos...")
    db: Session = SessionLocal()
    try:
        watches = db.query(ProductWatch).filter(ProductWatch.is_active == True).all()
        if not watches:
            return
            
        monitored_groups = db.query(MonitoredGroup).all()
        for g in monitored_groups:
            try:
                entity = await client.get_entity(g.group_username_or_id)
                messages = await client.get_messages(entity, limit=10)
                for msg in messages:
                    await process_message(msg, db)
            except Exception as e:
                print(f"Erro ao buscar retroativo global no grupo {g.group_username_or_id}: {e}")
    finally:
        db.close()
    print("Varredura retroativa global concluída!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect telethon
    await client.connect()
    # verify if logged in
    if not await client.is_user_authorized():
        print("BOT NÃO AUTORIZADO! Por favor, rode 'python auth_telegram.py' primeiro.")
    else:
        print("Telethon Client Iniciado e Autenticado. Escutando mensagens...")
        asyncio.create_task(fetch_all_retroactive())
    
    yield
    
    await client.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get("/status")
def status():
    return {"status": "ok"}

@app.post("/trigger_retroactive/{product_id}")
async def trigger_retroactive(product_id: int):
    # Triggers background task to not block the response
    asyncio.create_task(fetch_retroactive(product_id))
    return {"message": "Varredura retroativa iniciada."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8090)
