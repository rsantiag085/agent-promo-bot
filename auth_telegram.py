import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    print("Erro: TELEGRAM_API_ID ou TELEGRAM_API_HASH não encontrados no .env")
    exit(1)

# Garante que a pasta de dados exista antes de criar a sessão
os.makedirs("data", exist_ok=True)

client = TelegramClient('data/session', int(API_ID), API_HASH)

async def main():
    print("Iniciando processo de autenticação do Telegram...")
    # O comando start() pedirá automaticamente o número de telefone e o código via terminal
    await client.start()
    
    print("\n✅ Autenticação realizada com sucesso!")
    print("O arquivo 'session.session' foi criado.")
    print("Agora você já pode rodar o bot principal (bot.py) e iniciar o Streamlit!")

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
