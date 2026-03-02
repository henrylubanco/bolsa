import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

# 1. Configurações de Segurança
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 2. Dicionário Completo de Ativos [Baixa, Alta]
monitorar = {
    "BGI=G": [320.00, 350.00],      # 🐂 Boi Gordo
    "USDBRL=X": [5.10, 5.40],       # 💵 Dólar Comercial
    "GOLD11.SA": [25.80, 30.00],    # ✨ Ouro
    "XPML11.SA": [106.00, 120.00],  # 🏢 FII XPML11
    "HGLG11.SA": [153.00, 170.00],  # 📦 FII HGLG11
    "KNCR11.SA": [100.00, 110.00],  # 📄 FII KNCR11
    "XPLG11.SA": [100.50, 105.00],  # 🏭 FII XPLG11
    "BTML11.SA": [85.00, 100.00],   # 🏬 FII BTML11
    "WEGE3.SA": [40.00, 60.00],     # ⚙️ Weg
    "GGBR4.SA": [20.00, 24.00],     # 🏦 Gerdau
    "ITUB4.SA": [39.00, 50.00],     # 🏦 Itaú
    "TOTS3.SA": [36.00, 39.00],     # 💻 Totvs
    "VGIA11.SA": [8.00, 11.00],     # 🚜 Fiagro
    "VISC11.SA": [107.20, 115.00],  # 🛍️ FII Shopping
    "MGLU3.SA": [8.00, 12.00]       # 🛒 Magalu
}

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro no Telegram: {e}")

def enviar_alerta(ativo, preco_atual, tipo):
    nomes = {
        "BGI=G": "🐂 Boi Gordo", "USDBRL=X": "💵 Dólar", "GOLD11.SA": "✨ Ouro",
        "XPML11.SA": "🏢 FII XPML11", "HGLG11.SA": "📦 FII HGLG11",
        "KNCR11.SA": "📄 FII KNCR11", "XPLG11.SA": "🏭 FII XPLG11",
        "WEGE3.SA": "⚙️ Weg", "ITUB4.SA": "🏦 Itaú"
    }
    nome = nomes.get(ativo, ativo)
    emoji = "📉" if tipo == "BAIXA" else "📈"
    msg = f"{emoji} *ALERTA DE {tipo}*\n\nAtivo: *{nome}*\nPreço: *R$ {preco_atual:.2f}*"
    enviar_mensagem(msg)

# --- INÍCIO DA EXECUÇÃO ---

# Configura hora de Brasília para o resumo
fuso = pytz.timezone('America/Sao_Paulo')
hora_agora = datetime.now(fuso)

# 1. RESUMO DAS 11H (Envia se for entre 11:00 e 11:15)
if hora_agora.hour == 11 and hora_agora.minute < 15:
    print("Enviando resumo das 11h...")
    try:
        # Busca preços para o resumo matinal
        boi_data = yf.Ticker("BGI=G").history(period="1d")
        usd_data = yf.Ticker("USDBRL=X").history(period="1d")
        
        if not boi_data.empty and not usd_data.empty:
            boi = boi_data['Close'].iloc[-1]
            usd = usd_data['Close'].iloc[-1]
            
            resumo = (
                f"🕒 *BOLETIM DAS 11:00h*\n\n"
                f"🐂 *Boi Gordo:* R$ {boi:.2f}\n"
                f"💵 *Dólar:* R$ {usd:.2f}\n\n"
                f"O mercado está aberto e o monitoramento de ativos segue ativo."
            )
            enviar_mensagem(resumo)
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")

# 2. MONITORAMENTO DE ALVOS (Roda sempre)
for ticker, alvos in monitorar.items():
    try:
        baixa, alta = alvos[0], alvos[1]
        df = yf.Ticker(ticker).history(period="1d")
        if df.empty: continue
        
        preco_atual = df['Close'].iloc[-1]
        
        if preco_atual <= baixa:
            enviar_alerta(ticker, preco_atual, "BAIXA")
        elif preco_atual >= alta:
            enviar_alerta(ticker, preco_atual, "ALTA")
            
    except Exception as e:
        print(f"Erro em {ticker}: {e}")

print("Monitoramento finalizado.")
