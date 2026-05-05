# Agent Promo Bot 🤖💸

Este é um bot automatizado construído em Python que monitora grupos do Telegram em busca de promoções específicas baseadas em palavras-chave e envia alertas em tempo real.

## 🚀 Como iniciar o projeto usando Docker

Siga o passo a passo abaixo para rodar a aplicação na sua máquina ou servidor.

### 1. Preparando as Variáveis de Ambiente
O bot precisa das suas credenciais do Telegram para funcionar.
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edite o arquivo `.env` com as suas chaves (`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_BOT_TOKEN`).

### 2. Autenticando o Telegram pela primeira vez
Antes de subir o bot em background, você precisa gerar o arquivo de sessão usando a sua conta do Telegram. Como estamos usando o Docker, você fará isso rodando o script de forma interativa:

```bash
# Faz o build da imagem e roda o script de autenticação no terminal
docker compose run --rm bot python auth_telegram.py
```
> Siga as instruções na tela (digite seu número de telefone com DDI e DDD e depois o código recebido no Telegram).

### 3. Rodando o Bot
Assim que a autenticação for concluída, a sessão e o banco de dados estarão salvos em segurança na pasta local `data/`. Agora, basta iniciar o bot em modo background:

```bash
docker compose up -d
```

### 📋 Comandos Úteis
* **Ver os logs do bot:** `docker compose logs -f`
* **Parar o bot:** `docker compose down`
* **Reiniciar o bot:** `docker compose restart`
