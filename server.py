from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pytz

app = FastAPI()

conversations = {}

class Message(BaseModel):
    device: str
    msg: str

def get_time():
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")

@app.get("/")
def home():
    return {"status": "Server OK", "time": get_time()}

@app.post("/chat")
def chat(data: Message):
    device = data.device
    msg = data.msg.strip()

    if device not in conversations:
        conversations[device] = []

    # lưu hội thoại nhưng giới hạn 50 dòng để không tràn RAM
    if len(conversations[device]) > 50:
        conversations[device].pop(0)

    conversations[device].append({"user": msg, "time": get_time()})

    reply = (
        "Lili đây 😎! Mình nghe rõ rồi nè.\n"
        "📌 Mình sẽ trả lời ngắn gọn, dễ hiểu nha.\n"
        "Bạn hỏi tiếp đi, Lili luôn sẵn sàng 😆"
    )

    conversations[device].append({"assistant": reply, "time": get_time()})

    return {
        "reply": reply,
        "mode": "normal",
        "time": get_time(),
        "history_length": len(conversations[device])
    }
