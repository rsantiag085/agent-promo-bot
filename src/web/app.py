import streamlit as st
import requests
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.database import SessionLocal, ProductWatch, AlertLog, MonitoredGroup

# Configurações da página
st.set_page_config(page_title="AgentAI Promo Dashboard", layout="wide")

# Inicialização do Banco
@st.cache_resource
def get_db():
    from src.core.database import init_db
    init_db()
    return SessionLocal()

db = get_db()

# --- Funções Auxiliares ---
def check_bot_status():
    try:
        response = requests.get("http://127.0.0.1:8090/status", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def trigger_retroactive(product_id):
    try:
        requests.post(f"http://127.0.0.1:8090/trigger_retroactive/{product_id}", timeout=3)
    except requests.exceptions.RequestException:
        pass # Falha silenciosa pra UI não quebrar se o bot estiver off

# --- Header ---
st.title("🎯 AgentAI Promo - Monitor Pessoal")
bot_online = check_bot_status()
if bot_online:
    st.success("🟢 Bot UserBot Status: ONLINE")
else:
    st.error("🔴 Bot UserBot Status: OFFLINE (Inicie o bot.py)")

st.divider()

# --- Layout ---
col1, col2 = st.columns([1, 1])

# --- Coluna 1: Watchlist ---
with col1:
    st.header("🛒 Sua Watchlist (Máx 5)")
    st.caption("Adicione os produtos que deseja monitorar e as palavras-chave correspondentes.")
    
    active_watches = db.query(ProductWatch).filter(ProductWatch.is_active).all()
    
    if len(active_watches) < 5:
        with st.form("add_watch_form"):
            new_name = st.text_input("Nome do Produto (Ex: iPhone 15)")
            new_keywords = st.text_input("Palavras-chave separadas por vírgula (Ex: iphone 15, apple iphone)")
            submitted = st.form_submit_button("➕ Adicionar à Watchlist")
            
            if submitted and new_name and new_keywords:
                new_watch = ProductWatch(product_name=new_name, keywords=new_keywords, is_active=True)
                db.add(new_watch)
                db.commit()
                # Dispara a varredura retroativa
                trigger_retroactive(new_watch.id)
                st.success(f"Produto {new_name} adicionado e varredura retroativa iniciada!")
                st.rerun()
    else:
        st.warning("⚠️ Limite de 5 produtos ativos atingido.")

    # Lista atual
    for watch in active_watches:
        with st.expander(f"📌 {watch.product_name}"):
            st.write(f"**Palavras-Chave:** {watch.keywords}")
            if st.button("❌ Remover", key=f"rm_{watch.id}"):
                db.delete(watch) # Para fins práticos, estamos deletando
                db.commit()
                st.rerun()

# --- Coluna 2: Grupos Monitorados e Logs ---
with col2:
    st.header("👥 Grupos Alvo")
    st.caption("Adicione os usernames ou IDs dos grupos/canais que deseja escutar.")
    
    groups = db.query(MonitoredGroup).all()
    group_list = ", ".join([g.group_username_or_id for g in groups])
    st.info(f"Monitorando atualmente: {group_list if group_list else 'Nenhum'}")
    
    with st.form("add_group_form"):
        new_group = st.text_input("Username ou ID do chat (Ex: @promocoesbr ou -100123456)")
        submitted_grp = st.form_submit_button("Adicionar Grupo")
        if submitted_grp and new_group:
            # limpar @ se houver para evitar duplo @ não processado, ou manter
            # o telethon entende com ou sem @, mas padronizando:
            if not db.query(MonitoredGroup).filter(MonitoredGroup.group_username_or_id == new_group).first():
                db.add(MonitoredGroup(group_username_or_id=new_group))
                db.commit()
                st.rerun()
    
    if groups:
        if st.button("🗑️ Limpar Todos os Grupos"):
            db.query(MonitoredGroup).delete()
            db.commit()
            st.rerun()

st.divider()

# --- Logs Recentes ---
st.header("📜 Histórico de Alertas (Últimos 20)")
logs = db.query(AlertLog).order_by(AlertLog.timestamp.desc()).limit(20).all()

if not logs:
    st.info("Nenhuma promoção detectada ainda.")
else:
    # Preparar dados para Tabela
    data = []
    for log in logs:
        # Puxa o nome para ficar mais legível
        prod = db.query(ProductWatch).filter(ProductWatch.id == log.product_id).first()
        prod_name = prod.product_name if prod else "Desconhecido"
        
        data.append({
            "Data/Hora": log.timestamp.strftime("%d/%m/%Y %H:%M"),
            "Produto": prod_name,
            "Preço": log.price_found,
            "Link": log.original_link,
            "Fonte": log.group_id
        })
        
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
