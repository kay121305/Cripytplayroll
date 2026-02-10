import telebot
from collections import deque, Counter

# ================= CONFIG =================
API_TOKEN = "8518534286:AAFbWZqBArVMK31GD06vRR9YJOG5fxuFwnM"
CRIPTOPLAY_BOT_ID = 8431121309

bot = telebot.TeleBot(API_TOKEN)

# ================= DADOS =================
usuarios = {}            # user_id -> banca
ultimos_30 = deque(maxlen=30)

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "💼 *Gestão de Banca — Criptoplay*\n\n"
        "Informe o valor da sua banca.\n"
        "Exemplo: `67`",
        parse_mode="Markdown"
    )

# ================= RECEBE BANCA =================
@bot.message_handler(func=lambda m: m.text.isdigit())
def receber_banca(msg):
    banca = float(msg.text)
    usuarios[msg.from_user.id] = banca

    bot.send_message(
        msg.chat.id,
        f"✅ Banca registrada: *R$ {banca:.2f}*\n\n"
        "Aguarde os sinais.",
        parse_mode="Markdown"
    )

# ================= RECEBE NÚMEROS (HISTÓRICO) =================
@bot.message_handler(func=lambda m: m.text.isdigit() and 0 <= int(m.text) <= 36)
def registrar_numero(msg):
    n = int(msg.text)
    ultimos_30.append(n)

    if len(ultimos_30) == 30:
        enviar_tabela(msg.chat.id)

# ================= TABELA 30 RODADAS =================
def enviar_tabela(chat_id):
    contagem = Counter(ultimos_30)
    linhas = []

    for i in range(37):
        linhas.append(f"{i:>2} → {contagem.get(i,0)}x")

    texto = "📊 *ESTATÍSTICA — ÚLTIMAS 30*\n\n"
    for i in range(0, 37, 3):
        texto += " | ".join(linhas[i:i+3]) + "\n"

    bot.send_message(chat_id, texto, parse_mode="Markdown")

# ================= RECEBE SINAL DO CRIPTOPLAY =================
@bot.message_handler(func=lambda m: m.from_user.id == CRIPTOPLAY_BOT_ID)
def receber_sinal(msg):
    texto = msg.text

    if "3-6-9" in texto:
        estrategia = "3-6-9"
        qtd = 12
    elif "0-10" in texto:
        estrategia = "0-10"
        qtd = 10
    else:
        return

    for user_id, banca in usuarios.items():
        enviar_gestao(user_id, banca, estrategia, qtd)

# ================= GESTÃO =================
def enviar_gestao(user_id, banca, estrategia, qtd):
    fraca = 1
    media_total = banca / 2
    forte_total = banca

    media_num = media_total / qtd
    forte_num = forte_total / qtd

    bot.send_message(
        user_id,
        f"🎯 *SINAL {estrategia}*\n\n"
        f"💼 Banca: R$ {banca:.2f}\n\n"

        f"🟢 *FRACA*\n"
        f"R$ 1 por número\n"
        f"Risco baixo\n\n"

        f"🟡 *MÉDIA*\n"
        f"R$ {media_num:.2f} por número\n"
        f"Usa meia banca\n\n"

        f"🔴 *AGRESSIVA*\n"
        f"R$ {forte_num:.2f} por número\n"
        f"Usa banca total\n\n"

        f"📌 *Sugestão:* escolha conforme o momento\n"
        f"⚠️ Nunca misture estratégias",
        parse_mode="Markdown"
    )

print("🤖 Bot de Gestão Criptoplay rodando...")
bot.infinity_polling()
