import os
from telethon.sync import TelegramClient
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    print("ERRO: TELEGRAM_API_ID e TELEGRAM_API_HASH não encontrados no .env")
    print("Por favor, preencha o arquivo .env com suas credenciais do my.telegram.org")
    exit(1)

# Nome do arquivo de sessão será session.session
SESSION_NAME = 'session'

print("Iniciando processo de autenticação do Telegram UserBot...")
print("Será solicitado o seu número de telefone (com DDI e DDD, ex: +5511999999999) e o código recebido no app.\n")

with TelegramClient(SESSION_NAME, int(API_ID), API_HASH) as client:
    print("\n--- Autenticação Bem Sucedida! ---")
    print("O arquivo session.session foi gerado na raiz do projeto.")
    print("Agora você pode rodar o bot (python bot.py) ou o painel Streamlit.")
