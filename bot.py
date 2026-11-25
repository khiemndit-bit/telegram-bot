from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import os
TOKEN = os.environ.get("9109730930:AAF3sLwMrurUH1NEPJUeFapgdZ9Dr8s2BhY")


CHON_CAU_HOI, CHON_LUA_CHON = range(2)

# --- CÁCH KHAI BÁO ĐÁP ÁN ---
# 1. Đáp án chữ: "giờ mở cửa": "Shop mở cửa..."
# 2. Đáp án ảnh: {"type": "photo", "file": "bang-gia.jpg", "caption": "Chú thích dưới ảnh"}
# 3. Đáp án có lựa chọn 1/2: như bên dưới

QA = {


# VÍ DỤ 1: Câu hỏi -> Hỏi thêm Lựa chọn 1/2 -> Trả lời bằng ẢNH
    "Tôi muốn tải app X-Poker": {
        "cau_hoi_phu": "Bạn sử dụng điện thoại nào?",
        "lua_chon": {
            "1. Iphone": {
                "type": "photo",
                "file": "huongdanip.jpg",
                "caption": "Bạn làm theo hướng dẫn như trong ảnh!"
            },
            "2. Android": "Bạn vào trang x-poker.net tải file apk về cài nha!",
        }
    },
   "Tôi muốn join CLB": "Bạn nhập đầy đủ 2 ID CLB và ID GT\nLine Malaysia 1k\nCLB RoyalCosmos\nID CLB 2292987\nID GT 3909651\n1 chip = 1k\nLine Malaysia 6k\nCLB Dream Poker 6\nID CLB 2225467\nID GT 3909651\n1 chip = 6k",

	"Tôi muốn nạp rút": "Hiện tại mình đang chỉ nhận nạp rút qua USDT, bạn liên hệ mình qua kênh tele https://t.me/hotroxpoker để mình hỗ trợ ",



    

    "Tôi muốn giao dịch qua USDT": {
        "cau_hoi_phu": "Bạn đã có ví USDT chưa?",
        "lua_chon": {
            "1. Đã có ví USDT": "Bạn liên hệ mình qua kênh tele https://t.me/hotroxpoker để mình hỗ trợ ",
            "2. Chưa có ví USDT": "Bạn tải cái binance về sau đó tạo tk và KYC là đc, vướng đâu liên hệ mình qua kênh tele https://t.me/hotroxpoker để mình hỗ trợ ",
        }
    },
}

# Hàm gửi đáp án - tự biết là chữ hay ảnh
async def gui_dap_an(update: Update, dap_an):
    # Nếu đáp án là ảnh
    if isinstance(dap_an, dict) and dap_an.get("type") == "photo":
        try:
            with open(dap_an["file"], "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=dap_an.get("caption", "")
                )
        except FileNotFoundError:
            await update.message.reply_text(f"Lỗi: Không tìm thấy file ảnh {dap_an['file']}. Bạn kiểm tra lại tên file nhé!")
    else:
        # Nếu đáp án là chữ
        await update.message.reply_text(dap_an)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[q] for q in QA.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Chào bạn đến với hỗ trợ tự động về X-Poker! Bạn muốn hỏi gì?\nBấm 1 câu hỏi bên dưới nhé:", reply_markup=reply_markup)
    return CHON_CAU_HOI

async def chon_cau_hoi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    cau_hoi_goc = None
    for q in QA.keys():
        if q.lower() == user_text:
            cau_hoi_goc = q
            break
    
    if not cau_hoi_goc:
        await update.message.reply_text("Bạn bấm 1 câu hỏi trong danh sách giúp mình nhé!")
        return CHON_CAU_HOI

    data = QA[cau_hoi_goc]
    context.user_data['cau_hoi_dang_chon'] = cau_hoi_goc

    # Trường hợp: Trả lời luôn (chữ hoặc ảnh)
    if isinstance(data, str) or (isinstance(data, dict) and data.get("type") == "photo"):
        await gui_dap_an(update, data)
        await update.message.reply_text("Bạn muốn hỏi thêm gì nữa không?")
        return CHON_CAU_HOI

    # Trường hợp: Cần hỏi thêm Lựa chọn 1/2
    keyboard = [[lc] for lc in data["lua_chon"].keys()]
    keyboard.append(["⬅️ Quay lại"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(data["cau_hoi_phu"], reply_markup=reply_markup)
    return CHON_LUA_CHON

async def chon_lua_chon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if user_text == "⬅️ Quay lại":
        return await start(update, context)

    cau_hoi_goc = context.user_data.get('cau_hoi_dang_chon')
    lua_chon_dict = QA[cau_hoi_goc]["lua_chon"]

    dap_an = None
    for lc, ans in lua_chon_dict.items():
        if lc.lower() == user_text.lower():
            dap_an = ans
            break
    
    if dap_an is None:
        await update.message.reply_text("Bạn bấm 1 trong 2 lựa chọn giúp mình nhé!")
        return CHON_LUA_CHON

    await gui_dap_an(update, dap_an)
    
    keyboard = [[q] for q in QA.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Bạn muốn hỏi thêm gì nữa không?", reply_markup=reply_markup)
    return CHON_CAU_HOI

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHON_CAU_HOI: [MessageHandler(filters.TEXT & ~filters.COMMAND, chon_cau_hoi)],
            CHON_LUA_CHON: [MessageHandler(filters.TEXT & ~filters.COMMAND, chon_lua_chon)],
        },
        fallbacks=[],
        allow_reentry=True
    )
    app.add_handler(conv)
    print("Bot đang chạy...")
    app.run_polling()