import yfinance as yf
import requests
import os

# 1. Configurações de Segurança (GitHub Secrets)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 2. Dicionário Completo de Ativos
# Formato: "Ticker": [Alvo_Baixa, Alvo_Alta]
monitorar = {
    "BGI=F": [320.00, 340.00],      # 🐂 Boi Gordo
    "USDBRL=X": [5.10, 5.40],       # 💵 Dólar Comercial
    "GOLD11.SA": [25.80, 30.00],    # ✨ Ouro (Ref. Trend Ouro)
    "XPML11.SA": [106.00, 120.00],  # 🏢 FII XPML11
    "HGLG11.SA": [153.00, 170.00],  # 📦 FII HGLG11
    "KNCR11.SA": [100.00, 110.00],  # 📄 FII KNCR11
    "XPLG11.SA": [102.00, 115.00],  # 🏭 FII XPLG11
    "BTML11.SA": [85.00, 100.00],   # 🏬 FII BTML11
    "WEGE3.SA": [40.00, 60.00],     # ⚙️ Weg
    "ITUB4.SA": [39.00, 50.00],      # 🏦 Itaú
    "MGLU3.SA": [8.00, 12.00]      # 🏦 magalu
}

def enviar_alerta(ativo, preco_atual, tipo):
    nomes_amigaveis = {
        "BGI=F": "🐂 Arroba do Boi Gordo",
        "USDBRL=X": "💵 Dólar Comercial",
        "GOLD11.SA": "✨ Ouro (Ref. Trend Ouro)",
        "XPML11.SA": "🏢 FII XPML11 (Shoppings)",
        "HGLG11.SA": "📦 FII HGLG11 (Logística)",
        "KNCR11.SA": "📄 FII KNCR11 (Papel)",
        "XPLG11.SA": "🏭 FII XPLG11 (Galpões)",
        "BTML11.SA": "🏬 FII BTML11 (Varejo)",
        "WEGE3.SA": "⚙️ Weg (WEGE3)",
        "ITUB4.SA": "🏦 Itaú (ITUB4)"
    }
    
    nome_exibicao = nomes_amigaveis.get(ativo, ativo)
    emoji = "📉" if tipo == "BAIXA" else "📈"
    status = "ATINGIU LIMITE DE COMPRA" if tipo == "BAIXA" else "ATINGIU LIMITE DE VENDA"

    mensagem = (
        f"{emoji} *ALERTA DE {tipo}*\n\n"
        f"Ativo: *{nome_exibicao}*\n"
        f"Preço Atual: *R$ {preco_atual:.2f}*\n\n"
        f"📢 *Status:* {status}"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro no Telegram: {e}")

# 3. Lógica de Execução
print("Iniciando monitoramento completo...")

for ticker, alvos in monitorar.items():
    try:
        baixa, alta = alvos[0], alvos[1]
        ativo_yf = yf.Ticker(ticker)
        df = ativo_yf.history(period="1d")
        
        if df.empty:
            continue
            
        preco_atual = df['Close'].iloc[-1]
        print(f"Checando {ticker}: R$ {preco_atual:.2f}")

        if baixa and preco_atual <= baixa:
            enviar_alerta(ticker, preco_atual, "BAIXA")
        elif alta and preco_atual >= alta:
            enviar_alerta(ticker, preco_atual, "ALTA")
            
    except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")

print("Monitoramento finalizado com sucesso!")
