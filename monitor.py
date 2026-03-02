import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

# 1. Configurações de Segurança
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 2. Dicionário de Ativos [Baixa, Alta]
monitorar = {
    "BGI=G": [320.00, 350.00],      # 🐂 Boi Gordo
    "USDBRL=X": [5.10, 5.40],       # 💵 Dólar Comercial
    "GOLD11.SA": [25.80, 30.00],    # ✨ Ouro
    "XPML11.SA": [106.00, 120.00],  # 🏢 FII XPML11
    "HGLG11.SA": [153.00, 170.00],  # 📦 FII HGLG11
    "KNCR11.SA": [100.00, 110.00],  # 📄 FII KNCR11
    "XPLG11.SA": [100.50, 105.00],  # 🏭 FII XPLG11
    "BTML11.SA": [85.00, 102.00],   # 🏬 FII BTML11
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

# Configura fuso horário de Brasília
fuso = pytz.timezone('America/Sao_Paulo')
hora_agora = datetime.now(fuso)

# --- LOGICA DE HORÁRIOS ---

# 1. CHECK-IN DE STATUS (08:00h)
if hora_agora.hour == 8 and hora_agora.minute < 15:
    msg_status = "✅ *SISTEMA ONLINE*\n\nBom dia! O monitor de ativos da Fazenda e Bolsa iniciou com sucesso e está operante."
    enviar_mensagem(msg_status)

# 2. RESUMO MATINAL (11:00h)
elif hora_agora.hour == 11 and hora_agora.minute < 15:
    try:
        boi = yf.Ticker("BGI=G").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
        resumo = f"🕒 *BOLETIM 11:00h*\n\n🐂 *Boi:* R$ {boi:.2f}\n💵 *Dólar:* R$ {usd:.2f}"
        enviar_mensagem(resumo)
    except:
        pass

# 3. MONITORAMENTO DE ALVOS (Roda em todas as execuções)
for ticker, alvos in monitorar.items():
    try:
        baixa, alta = alvos[0], alvos[1]
        df = yf.Ticker(ticker).history(period="1d")
        if df.empty: continue
        
        preco_atual = df['Close'].iloc[-1]
        
        if preco_atual <= baixa:
            enviar_mensagem(f"📉 *ALERTA DE BAIXA*\nAtivo: {ticker}\nPreço: *R$ {preco_atual:.2f}*")
        elif preco_atual >= alta:
            enviar_mensagem(f"📈 *ALERTA DE ALTA*\nAtivo: {ticker}\nPreço: *R$ {preco_atual:.2f}*")
    except Exception as e:
        print(f"Erro em {ticker}: {e}")
