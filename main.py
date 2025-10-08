import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === 환경변수 불러오기 ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip().isdigit()]

print("🔑 BOT_TOKEN:", BOT_TOKEN[:10] + "..." if BOT_TOKEN else "❌ 없음")
print("👮 ADMIN_IDS:", ADMIN_IDS)

if not BOT_TOKEN:
    print("❌ BOT_TOKEN이 없습니다. Render 환경변수를 확인하세요.")
if not ADMIN_IDS:
    print("⚠️ ADMIN_IDS가 비어있습니다.")

# === 유저 상태 저장 ===
user_state = {}

WELCOME_TEXT = """
[김평범이 드리는 마지막 선물 안내]

안녕하세요, 김평범 입니다.
VIPACCESS를 받고 싶으시면 아래 "VIPACCESS 받는 방법"을 누르고 그대로 따라해주세요

추가 문의사항이 있으시거나 이미 OKX 계정이 있으시다면 "상담원 연결" 버튼을 누르고 말씀해주세요!

────────────────
✅ 김평범이 드리는 마지막 편지 보러가기 
https://buly.kr/FWTlJiF

────────────────
✅ VIPACCESS 받는 방법
https://buly.kr/7QMuCBn

감사합니다.
"""

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("VIPACCESS 받는 방법")],
        [KeyboardButton("상담원 연결")]
    ],
    resize_keyboard=True
)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"➡️ /start 호출됨: user={update.effective_user.id}")
    uid = update.effective_user.id
    uname = update.effective_user.username or str(uid)
    user_state.setdefault(uid, {"username": uname, "mode": "auto"})
    await update.message.reply_text(WELCOME_TEXT, disable_web_page_preview=True, reply_markup=MAIN_MENU)

# === /id ===
async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"➡️ /id 호출됨: user={update.effective_user.id}")
    uid = update.effective_user.id
    await update.message.reply_text(f"당신의 텔레그램 ID: {uid}")

# === 일반 메시지 처리 ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()
    uname = update.effective_user.username or str(uid)

    print(f"📩 메시지 수신: {uname}({uid}): {text}")

    if uid not in user_state:
        user_state[uid] = {"username": uname, "mode": "auto"}

    if text == "VIPACCESS 받는 방법":
        await update.message.reply_text("👉 아래 링크를 따라하시면 됩니다:\nhttps://buly.kr/7QMuCBn")
        return

    if text == "상담원 연결":
        user_state[uid]["mode"] = "human"
        await update.message.reply_text("🙋 상담원을 연결해드리겠습니다. 잠시만 기다려주세요!")
        for admin in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin, text=f"📥 [상담요청] 고객 {uname}({uid})가 상담원 연결을 요청했습니다.")
        return

    if user_state[uid]["mode"] == "human" and uid not in ADMIN_IDS:
        for admin in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin, text=f"[고객 {uname}({uid})]\n{text}")
        await update.message.reply_text("📨 메시지를 전달했습니다.")
        return

    await update.message.reply_text(WELCOME_TEXT, disable_web_page_preview=True, reply_markup=MAIN_MENU)

# === 메인 실행 ===
def main():
    print("🚀 텔레그램 봇 실행 준비 중...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 봇 실행 시작 (Polling)...")
    app.run_polling()

if __name__ == "__main__":
    print("📡 main.py 시작됨")
    main()

