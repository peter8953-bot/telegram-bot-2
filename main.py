import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === 환경변수 ===
BOT_TOKEN = os.environ["8202889233:AAESSQZDBwxHiNZcsQr8F2pO14ZSIEKfYO0"]     # Render Environment에 BOT_TOKEN 등록 필수
# 여러 관리자 아이디 (쉼표로 구분하여 입력 가능)
ADMIN_IDS = [1007406034, 7111088595]    # 관리자 2명 (정수형 ID로)

# === 유저 상태 저장 ===
user_state = {}

# === 웰컴메세지 ===
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

# === 버튼 메뉴 ===
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
        await update.message.reply_text("👉 아래 링크의 내용을 확인하시고 등록절차를 그대로 따라하시면 됩니다:\nhttps://buly.kr/7QMuCBn")
        return

    # 버튼 2: 상담원 연결
    if text == "상담원 연결":
        user_state[uid]["mode"] = "human"
        await update.message.reply_text("🙋 상담원을 연결해드리겠습니다. 잠시만 기다려주세요!")
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📥 [상담요청] 고객 {uname}({uid})가 상담원 연결을 요청했습니다."
            )
        return

    # 고객 메시지 → 관리자들에게 전달
    if user_state[uid]["mode"] == "human" and uid not in ADMIN_IDS:
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin_id, text=f"[고객 {uname}({uid})]\n{text}")
        await update.message.reply_text("📨 메시지를 전달했습니다.")
        return

    # 기본 응답
    await update.message.reply_text(WELCOME_TEXT, disable_web_page_preview=True, reply_markup=MAIN_MENU)

# === 관리자 명령 ===
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("관리자만 사용 가능합니다.")
    try:
        target_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text="👨‍💼 상담원: " + reply_text, reply_markup=MAIN_MENU)

        # 다른 관리자에게도 전달 내역 알림
        for admin_id in ADMIN_IDS:
            if admin_id != update.effective_user.id:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📤 [{update.effective_user.first_name}] 고객({target_id})에게 보낸 메세지:\n{reply_text}"
                )

        await update.message.reply_text("✅ 고객에게 답변을 보냈습니다.")
    except Exception as e:
        await update.message.reply_text(f"사용법: /reply <유저ID> <메시지>\n에러: {e}")

async def admin_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("관리자만 사용 가능합니다.")
    try:
        target_id = int(context.args[0])
        if target_id in user_state:
            user_state[target_id]["mode"] = "auto"
        await context.bot.send_message(chat_id=target_id, text="상담이 종료되었습니다. 자동응답 모드로 전환되었습니다.", reply_markup=MAIN_MENU)
        await update.message.reply_text(f"✅ {target_id} 고객을 자동응답 모드로 전환했습니다.")
    except Exception as e:
        await upda

