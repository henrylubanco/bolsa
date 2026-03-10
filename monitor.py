import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

# --- CONFIGURAÇÕES DE AMBIENTE ---
# Uso de variáveis de ambiente para segurança (Boas práticas de DevOps)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# --- CONFIGURAÇÃO DE ATIVOS [ALVO_BAIXA, ALVO_ALTA] ---
# Estrutura de dicionário para facilitar a iteração e manutenção
monitorar = {
    "BGI=G": [320.00, 350.00],      # 🐂 Boi Gordo (Contrato Futuro)
    "USDBRL=X": [5.10, 5.40],       # 💵 Dólar Comercial
    "GOLD11.SA": [25.80, 30.00],    # ✨ Ouro
    "XPML11.SA": [106.00, 120.00],  # 🏢 FII XPML11
    "HGLG11.SA": [153.00, 170.00],  # 📦 FII HGLG11
    "KNCR11.SA": [100.00, 110.00],  # 📄 FII KNCR11
    "XPLG11.SA": [100.50, 105.00],  # 🏭 FII XPLG11
    "BTML11.SA": [85.00, 102.00],   # 🏬 FII BTML11
    "WEGE3.SA": [40.00, 60.00],     # ⚙️ Weg
    "GGBR4.SA": [16.00, 24.00],     # 🏦 Gerdau
    "ITUB4.SA": [39.00, 50.00],     # 🏦 Itaú
    "TOTS3.SA": [35.00, 39.00],     # 💻 Totvs
    "VGIA11.SA": [8.00, 11.00],     # 🚜 Fiagro
    "VISC11.SA": [107.20, 115.00],  # 🛍️ FII Shopping
    "MGLU3.SA": [8.00, 12.00]       # 🛒 Magalu
}

def enviar_mensagem(texto):
    """Encapsula a chamada da API do Telegram com tratamento de exceção."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status() # Garante que erros 4xx ou 5xx apareçam no log
    except Exception as e:
        print(f"Falha na comunicação com Telegram: {e}")

def obter_preco(ticker):
    """Busca o preço atualizado. Fallback para evitar falhas em ativos de baixa liquidez."""
    try:
        ativo = yf.Ticker(ticker)
        # Tenta pegar o último preço do dia
        df = ativo.history(period="1d")
        if not df.empty:
            return df['Close'].iloc[-1]
        return None
    except Exception as e:
        print(f"Erro ao buscar ticker {ticker}: {e}")
        return None

# --- LÓGICA DE TEMPO E EXECUÇÃO ---

# Definição do fuso horário para evitar divergência com o servidor do GitHub (UTC)
fuso = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(fuso)
hora = agora.hour
minuto = agora.minute

print(f"Execução iniciada às {agora.strftime('%H:%M:%S')}")

# 1. CHECK-IN DE STATUS (Janela expandida para 30min para garantir execução no GitHub)
if hora == 8 and minuto <= 30:
    enviar_mensagem("✅ *SISTEMA ONLINE*\n\nO monitor de ativos está operante e vigiando o mercado.")

# 2. RESUMO MATINAL (Janela expandida para 30min)
elif hora == 11 and minuto <= 30:
    boi = obter_preco("BGI=G")
    usd = obter_preco("USDBRL=X")
    
    if boi and usd:
        resumo = (f"🕒 *BOLETIM 11:00h*\n\n"
                  f"🐂 *Boi:* R$ {boi:.2f}\n"
                  f"💵 *Dólar:* R$ {usd:.2f}")
        enviar_mensagem(resumo)
    else:
        print("Falha ao coletar dados para o resumo matinal.")

# 3. MONITORAMENTO DE ALVOS (Execução principal)
for ticker, alvos in monitorar.items():
    preco = obter_preco(ticker)
    
    if preco:
        baixa, alta = alvos[0], alvos[1]
        if preco <= baixa:
            enviar_mensagem(f"📉 *ALERTA DE BAIXA*\nAtivo: `{ticker}`\nPreço: *R$ {preco:.2f}*")
        elif preco >= alta:
            enviar_mensagem(f"📈 *ALERTA DE ALTA*\nAtivo: `{ticker}`\nPreço: *R$ {preco:.2f}*")

print("Execução finalizada.")
