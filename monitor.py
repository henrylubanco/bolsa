import yfinance as yf
import requests
import os

# Configurações vindas do GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Dicionário de ativos: "Ticker.SA": Preço_Alvo
# O alerta dispara se o preço for MENOR ou IGUAL ao alvo
monitorar = {
    "XPML11.SA": 115.00,
    "HGLG11.SA": 165.00,
    "KNCR11.SA": 102.00,
    "WEGE3.SA": 38.50,
    "ITUB4.SA": 32.00,
    "BTML11.SA": 95.00  # Adicione outros conforme precisar
}

def enviar_alerta(ativo, preco):
    mensagem = f"⚠️ *ALERTA DE PREÇO*\n\nO ativo *{ativo}* atingiu R$ {preco:.2f}!\nEstá abaixo do seu preço alvo configurado."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

for ticker, alvo in monitorar.items():
    try:
        dados = yf.Ticker(ticker)
        # Pega o último preço de fechamento
        preco_atual = dados.history(period="1d")['Close'].iloc[-1]
        
        print(f"Checando {ticker}: Atual R$ {preco_atual:.2f} | Alvo R$ {alvo:.2f}")
        
        if preco_atual <= alvo:
            enviar_alerta(ticker, preco_atual)
            
    except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")
