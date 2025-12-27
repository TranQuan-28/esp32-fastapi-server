from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

conversations = {}

class Message(BaseModel):
    device: str
    msg: str

def get_time():
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

@app.post("/chat")
def chat(data: Message):
    device = data.device
    msg = data.msg.strip()

    if device not in conversations:
        conversations[device] = []

    conversations[device].append({"user": msg, "time": get_time()})

    # ---------- AI logic đơn giản ----------
    reply = (
        "Lili đây 😎! Mình nghe rồi nha.\n"
        "📌 Trả lời nhanh gọn: mình đang sẵn sàng giúp bạn.\n"
        "Bạn hỏi tiếp đi, mình không nhắc lại câu hỏi của bạn nữa đâu 😆"
    )

    conversations[device].append({"assistant": reply, "time": get_time()})

    return {
        "reply": reply,
        "mode": "normal",
        "time": get_time(),
        "history_length": len(conversations[device])
    }
