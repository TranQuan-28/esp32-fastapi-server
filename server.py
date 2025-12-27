from fastapi import FastAPI
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from datetime import datetime

app = FastAPI()

conversations = {}
translate_mode = {}

class Message(BaseModel):
    device: str
    msg: str

def get_time():
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

def translate_text(text, dest="vi"):
    try:
        return GoogleTranslator(source="auto", target=dest).translate(text)
    except:
        return text

@app.post("/chat")
def chat(data: Message):
    device = data.device
    msg = data.msg

    if device not in conversations:
        conversations[device] = []
        translate_mode[device] = False

    conversations[device].append({"user": msg, "time": get_time()})

    # ---------------- AI logic ----------------
    reply = f"Lili đây nè 😆! Nghe bạn nói: '{msg}' mà vui ghê luôn!\n" \
            f"Tôi luôn sẵn sàng giúp bạn, hỏi gì cứ quăng ra nha! ✨"

    conversations[device].append({"assistant": reply, "time": get_time()})

    return {
        "reply": reply,
        "mode": "translate" if translate_mode[device] else "normal",
        "time": get_time(),
        "history_length": len(conversations[device])
    }
