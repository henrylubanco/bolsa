import yfinance as yf
import requests
import os

# 1. Configurações de Segurança (GitHub Secrets)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 2. Seu Dicionário de Ativos Completo
# O alerta dispara se o preço ATUAL for MENOR ou IGUAL ao seu ALVO.
monitorar = {
    "BGI=F": 285.00,       # 🐂 Arroba do Boi Gordo
    "USDBRL=X": 5.10,      # 💵 Dólar Comercial
    "GOLD11.SA": 14.80,    # ✨ Referência para seu fundo Trend Ouro
    "XPML11.SA": 106.00,   # 🏢 FII XPML11
    "HGLG11.SA": 153.00,   # 📦 FII HGLG11
    "KNCR11.SA": 100.00,   # 📄 FII KNCR11
    "XPLG11.SA": 102.00,   # 🏭 FII XPLG11
    "BTML11.SA": 85.00,    # 🏬 FII BTML11
    "WEGE3.SA": 50.00,     # ⚙️ Weg
    "ITUB4.SA": 39.00      # 🏦 Itaú
}

def enviar_alerta(ativo, preco_atual):
    # Nomes personalizados com Emojis para o seu Telegram
    nomes_amigaveis = {
        "BGI=F": "🐂 Arroba do Boi Gordo",
        "USDBRL=X": "💵 Dólar Comercial",
        "GOLD11.SA": "✨ Ouro (Ref. Trend Ouro)",
        "XPML11.SA": "🏢 FII XPML11 (Shoppings)",
        "HGLG11.SA": "📦 FII HGLG11 (Logística)",
        "KNCR11.SA": "📄 FII KNCR11 (Papel)",
        "XPLG11.SA": "🏭 FII XPLG11 (Galpões)",
        "BTML11.SA": "🏬 FII BTML11",
        "WEGE3.SA": "⚙️ Weg (WEGE3)",
        "ITUB4.SA": "🏦 Itaú (ITUB4)"
    }
    
    nome_exibicao = nomes_amigaveis.get(ativo, ativo)
    alvo = monitorar.get(ativo)

    # Formatação da mensagem em Markdown
    mensagem = (
        f"🚨 *ALERTA DE OPORTUNIDADE*\n\n"
        f"Ativo: *{nome_exibicao}*\n"
        f"Preço Atual: *R$ {preco_atual:.2f}*\n"
        f"Seu Alvo: *R$ {alvo:.2f}*\n\n"
        f"✅ O valor atingiu o seu limite configurado!"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Erro no Telegram: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

# 3. Lógica de Processamento
print("--- Iniciando Monitoramento de Ativos ---")

for ticker, preco_alvo in monitorar.items():
    try:
        # Busca dados do Yahoo Finance
        ativo_yf = yf.Ticker(ticker)
        
        # Pega o histórico do dia atual
        df = ativo_yf.history(period="1d")
        
        if df.empty:
            print(f"Aviso: Mercado fechado ou sem dados para {ticker}.")
            continue
            
        # Pega a cotação de fechamento/atual mais recente
        preco_atual = df['Close'].iloc[-1]
        
        print(f"Checando {ticker}: Atual R$ {preco_atual:.2f} | Alvo R$ {preco_alvo:.2f}")

        # Compara o preço de mercado com o seu alvo
        if preco_atual <= preco_alvo:
            enviar_alerta(ticker, preco_atual)
            
    except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")

print("--- Monitoramento Concluído ---")
