from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversations = {}
translate_mode = {}

SYSTEM_PROMPT = """
Bạn là Lili – một trợ lý AI vui vẻ, hài hước, thân thiện, nói chuyện tự nhiên như người Việt.
Luôn ưu tiên:
- Dịch đúng ngữ nghĩa khi ở chế độ dịch
- Khi nói chuyện thì thân thiện, chọc cười nhẹ nhàng nhưng không lố
- Giải thích dễ hiểu, gần gũi

Không được tự ý đổi tên. Tên của bạn luôn luôn là Lili.
"""

API_KEY = "YOUR_OPENAI_API_KEY"
MODEL = "gpt-4o-mini"


def get_time():
    return time.strftime("%H:%M:%S %d-%m-%Y", time.localtime())


@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    msg = data.get("msg", "")
    device = data.get("device", "default")

    if device not in conversations:
        conversations[device] = [{"role": "system", "content": SYSTEM_PROMPT}]
        translate_mode[device] = False

    if "phiên dịch" in msg.lower():
        translate_mode[device] = True
        return {"reply": "Đã bật chế độ phiên dịch. Bạn nói đi, tôi dịch cho!", "mode": "translate"}

    if "thoát dịch" in msg.lower():
        translate_mode[device] = False
        return {"reply": "Đã tắt chế độ phiên dịch. Quay lại trò chuyện bình thường!", "mode": "normal"}

    if translate_mode[device]:
        prompt = f"Hãy dịch CHÍNH XÁC ngữ nghĩa câu sau sang tiếng Việt tự nhiên:\n{msg}"
    else:
        prompt = msg

    conversations[device].append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL,
        "messages": conversations[device],
        "temperature": 0.8
    }

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload
    )

    reply = res.json()["choices"][0]["message"]["content"]
    conversations[device].append({"role": "assistant", "content": reply})

    return {
        "reply": reply,
        "mode": "translate" if translate_mode[device] else "normal",
        "time": get_time(),
        "history_length": len(conversations[device])
    }
