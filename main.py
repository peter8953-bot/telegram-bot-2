import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === 환경변수 ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")          # Render 환경변수에 BOT_TOKEN 등록 필수
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # 관리자 ID 하나만 사용

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
    uid = update.effective_user.id
    uname = update.effective_user.username or str(uid)
    user_state.setdefault(uid, {"username": uname, "mode": "auto"})
    await update.message.reply_text(WELCOME_TEXT, disable_web_page_preview=True, reply_markup=MAIN_MENU)

# === /id ===
async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"당신의 텔레그램 ID: {uid}")

# === 일반 메시지 처리 ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()
    uname = update.effective_user.username or str(uid)

    if uid not in user_state:
        user_state[uid] = {"username": uname, "mode": "auto"}

    # 버튼 1: VIPACCESS
    if text == "VIPACCESS 받는 방법":
        await update.message.reply_text("👉_

