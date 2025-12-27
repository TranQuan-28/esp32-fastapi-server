from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pytz
from googletrans import Translator

app = FastAPI()

class ChatMessage(BaseModel):
    device_id: str
    msg: str

translator = Translator()

# Lưu hội thoại theo từng thiết bị
conversations = {}
translate_mode = {}

def get_time():
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(tz).strftime("%H:%M:%S - %d/%m/%Y")

@app.get("/")
def home():
    return {
        "status": "Lili đang trực chiến nè 😎",
        "time": get_time()
    }

@app.post("/chat")
def chat(data: ChatMessage):
    device = data.device_id
    text = data.msg.strip()
    lower = text.lower()

    if device not in conversations:
        conversations[device] = []
    if device not in translate_mode:
        translate_mode[device] = False

    # ====== TẮT DỊCH ======
    if any(k in lower for k in ["thoát", "thoat", "normal", "bình thường", "binh thuong"]):
        translate_mode[device] = False
        reply = "Lili thoát chế độ dịch rồi nè 🎧. Giờ tám chuyện bình thường thôi 😆"

    # ====== BẬT DỊCH ======
    elif "dịch" in lower or "phiên dịch" in lower:
        translate_mode[device] = True
        reply = "Đã bật chế độ phiên dịch 🧠✨. Cứ nói, Lili lo phần dịch!"

    # ====== ĐANG DỊCH ======
    elif translate_mode[device]:
        try:
            translated = translator.translate(text, dest='en')
            reply = f"🔁 Dịch sang English: {translated.text}"
        except:
            reply = "Hình như mạng server hơi lag 😅. Thử lại nha."

    # ====== HỎI GIỜ ======
    elif "mấy giờ" in lower or "thời gian" in lower or "ngày" in lower:
        reply = f"Bây giờ là {get_time()} ⏰ — giờ Việt Nam chuẩn luôn 😎"

    # ====== CHÀO HỎI ======
    elif "chào" in lower or "hello" in lower or "hi" in lower:
        reply = "Hellooo 😆! Mình là Lili — AI cute nhưng nói chuyện mặn mà lắm nha 😎"

    # ====== TRẢ LỜI THƯỜNG ======
    else:
        reply = f"Lili nghe rồi 😏: “{text}”. Nghe thú vị đó, kể thêm đi coi sao 🤭"

    # Lưu lịch sử nhưng không trả ra
    conversations[device].append({
        "you": text,
        "lili": reply,
        "time": get_time()
    })

    return {
        "reply": reply,
        "mode": "translate" if translate_mode[device] else "normal",
        "time": get_time(),
        "history_length": len(conversations[device])
    }
