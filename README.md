# Agent Promo Bot 🤖💸

Este é um sistema automatizado construído em Python que monitora grupos do Telegram em busca de promoções específicas baseadas em palavras-chave e envia alertas em tempo real. Ele também conta com um painel web interativo para gerenciar palavras-chave e visualizar as promoções encontradas.

## ✨ Funcionalidades

*   **Monitoramento em Tempo Real**: Fica de olho em mensagens de grupos do Telegram e filtra as que contêm palavras-chave configuradas.
*   **Alertas Instantâneos**: Avisa quando uma promoção que você deseja é encontrada.
*   **Dashboard Web (Streamlit)**: Uma interface amigável para visualizar as promoções, adicionar/remover palavras-chave e gerenciar os grupos monitorados.
*   **Arquitetura Baseada em Contêineres**: Fácil de instalar e rodar usando Docker e Docker Compose.

## 🚀 Como iniciar o projeto usando Docker

Siga o passo a passo abaixo para rodar a aplicação na sua máquina ou servidor.

### 1. Preparando as Variáveis de Ambiente
O sistema precisa das suas credenciais do Telegram para funcionar.
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edite o arquivo `.env` com as suas chaves (`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_BOT_TOKEN` e demais necessárias).

### 2. Autenticando o Telegram pela primeira vez
Antes de subir a aplicação, você precisa gerar o arquivo de sessão usando a sua conta do Telegram. Como estamos usando o Docker, faça isso rodando o script de forma interativa:

```bash
# Faz o build da imagem e roda o script de autenticação no terminal
docker compose run --rm bot python auth_telegram.py
```
> Siga as instruções na tela (digite seu número de telefone com DDI e DDD e depois o código recebido no Telegram). A sessão ficará salva de forma segura na pasta local `data/`.

### 3. Iniciando a Aplicação
Agora, basta iniciar todos os serviços (Bot e Painel Web) em modo background:

```bash
docker compose up -d
```

### 4. Acessando o Dashboard
Com a aplicação rodando, você pode acessar o painel de controle pelo seu navegador:
*   **Acesse:** [http://localhost:8501](http://localhost:8501)

Lá você poderá gerenciar as palavras-chave que deseja monitorar e ver as últimas ofertas.

## 📁 Estrutura do Projeto

*   `src/bot/`: Código-fonte do bot do Telegram responsável pelo monitoramento.
*   `src/web/`: Aplicação web construída com Streamlit para o painel de controle.
*   `src/core/`: Módulos compartilhados entre o bot e a interface web (banco de dados, etc).
*   `auth_telegram.py`: Script de autenticação inicial do Telegram.
*   `data/`: Pasta onde o banco de dados e a sessão do Telegram são armazenados localmente (persistência via volumes do Docker).

## 📋 Comandos Úteis

*   **Ver os logs de todos os serviços:** `docker compose logs -f`
*   **Ver os logs só do bot:** `docker compose logs -f bot`
*   **Parar a aplicação:** `docker compose down`
*   **Reiniciar a aplicação:** `docker compose restart`
