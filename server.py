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
MAX_HISTORY = 50   # tránh tràn RAM server free

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

    # =====================
    #   TẮT CHẾ ĐỘ DỊCH
    # =====================
    if any(k in lower for k in ["thoát", "thoat", "normal", "bình thường", "binh thuong"]):
        translate_mode[device] = False
        reply = "Lili rời chế độ phiên dịch rồi nha 🎧. Quay lại tám chuyện vui vẻ thôi nào 😆"

    # =====================
    #   BẬT CHẾ ĐỘ DỊCH
    # =====================
    elif "dịch" in lower or "phiên dịch" in lower:
        translate_mode[device] = True
        reply = "Đã bật chế độ phiên dịch 🧠✨. Bạn nói gì cứ quăng vào đây, Lili lo hết!"

    # =====================
    #   ĐANG Ở CHẾ ĐỘ DỊCH
    # =====================
    elif translate_mode[device]:
        try:
            lang = translator.detect(text).lang
            if lang == "vi":
                translated = translator.translate(text, src='vi', dest='en')
            else:
                translated = translator.translate(text, dest='vi')
            reply = f"🔁 Dịch nè: {translated.text}"
        except:
            reply = "Ui da… mạng hơi lag 😅, dịch bị lỗi. Thử lại giùm Lili nha."

    # =====================
    #   HỎI NGÀY – GIỜ
    # =====================
    elif "mấy giờ" in lower or "giờ" in lower or "thời gian" in lower or "ngày" in lower:
        reply = f"Bây giờ là {get_time()} nha ⏰. Chuẩn không cần chỉnh luôn 😎"

    # =====================
    #   LỜI CHÀO
    # =====================
    elif "chào" in lower or "hello" in lower or "hi" in lower:
        reply = "Hellooo 😆! Mình là Lili — trợ lý AI vui tính, nhiệt tình và hơi lầy xíu. Có gì cứ hỏi nha!"

    # =====================
    #   TRẢ LỜI THÔNG MINH
    # =====================
    else:
        reply = f"Lili nghe rõ rồi 😏: “{text}”. Nghe có vẻ thú vị đó, kể thêm cho Lili nghe đi nè 🤭"

    # Lưu lịch sử (có giới hạn)
    conversations[device].append({"you": text, "lili": reply})
    if len(conversations[device]) > MAX_HISTORY:
        conversations[device].pop(0)

    # Chỉ trả câu trả lời cho ESP32
    return {"reply": reply}
