import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === 환경변수 ===
BOT_TOKEN = os.environ["BOT_TOKEN"]     # Render 환경변수에 넣으세요
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# === 유저 상태 저장 ===
user_state = {}

# === 웰컴메세지 ===
WELCOME_TEXT = """
[김평범이 드리는 마지막 선물 안내]

안녕하세요, 김평범 입니다.
제가 드리는 마지막 편지와 선물은 잘 받아 보셨나요?
추가 문의사항이 있으시면 "상담원 연결" 버튼을 눌러 편하게 말씀해주시고
김평범에게 남기고 싶은 말씀이 있으시다면 "편지 남기기"에 남겨주시기 바랍니다. 

────────────────
✅ 마지막 편지 보러가기 
https://www.notion.so/280ee3ec2d308025a75de2b65dde5414

────────────────
✅ 김평범의 마지막 선물 셀퍼럴 가입 방법
https://www.notion.so/280ee3ec2d308058983aed4f111d31af

감사합니다.
"""

# === 버튼 메뉴 ===
MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("셀퍼럴 가입방법")],
        [KeyboardButton("편지 남기기")],
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

    if text == "셀퍼럴 가입방법":
        await update.message.reply_text("👉 아래 링크를 따라하시면 됩니다:\nhttps://www.notion.so/280ee3ec2d308058983aed4f111d31af")
        return

    if text == "편지 남기기":
        user_state[uid]["mode"] = "human"
        await update.message.reply_text("지금 여기에 편지를 남겨주세요!")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 [편지] 고객 {uname}({uid})가 편지를 남겼습니다."
        )
        return

    if text == "상담원 연결":
        user_state[uid]["mode"] = "human"
        await update.message.reply_text("🙋 상담원을 연결해드리겠습니다. 잠시만 기다려주세요!")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 [상담요청] 고객 {uname}({uid})가 상담원 연결을 요청했습니다."
        )
        return

    if user_state[uid]["mode"] == "human" and uid != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"[고객 {uname}({uid})]\n{text}")
        await update.message.reply_text("📨 메시지를 전달했습니다.")
        return

    await update.message.reply_text(WELCOME_TEXT, disable_web_page_preview=True, reply_markup=MAIN_MENU)

# === 관리자 명령: /reply <유저ID> <메시지> ===
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("관리자만 사용 가능합니다.")
    try:
        target_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])  # ✅ 여기에서 오류 났던 부분 수정 완료
        await context.bot.send_message(
            chat_id=target_id,
            text="👨‍💼 상담원: " + reply_text,
            reply_markup=MAIN_MENU
        )
        await update.message.reply_text("✅ 고객에게 답변을 보냈습니다.")
    except Exception as e:
        await update.message.reply_text(f"사용법: /reply <유저ID> <메시지>\n에러: {e}")

