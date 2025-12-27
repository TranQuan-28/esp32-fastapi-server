from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import asyncio
from typing import Dict, List

API_KEY = "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"
client = Groq(api_key=API_KEY)

app = FastAPI()

# =========================
# STRUCTURE MEMORY
# =========================
class ChatMemory:
    def __init__(self):
        self.summary = (
            "Mini là trợ lý AI tiếng Việt, nói chuyện vui vẻ, thân thiện, "
            "đôi khi pha chút hài hước nhưng vẫn lịch sự và dễ hiểu."
        )
        self.history: List[Dict] = []

# lưu riêng cho từng user
user_sessions: Dict[str, ChatMemory] = {}

# =========================
# REQUEST BODY
# =========================
class Message(BaseModel):
    user_id: str
    msg: str


# =========================
# MAIN CHAT ROUTE
# =========================
@app.post("/chat")
async def chat(data: Message):
    try:
        # Tạo session cho user nếu chưa có
        if data.user_id not in user_sessions:
            user_sessions[data.user_id] = ChatMemory()

        session = user_sessions[data.user_id]

        # ====================
        # TẠO PROMPT
        # ====================
        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là Mini — trợ lý AI tiếng Việt, nói chuyện vui vẻ, hài hước nhẹ nhàng, "
                    "thân thiện, nhưng vẫn chính xác và dễ hiểu."
                )
            },
            {
                "role": "system",
                "content": f"Tóm tắt hội thoại trước đây: {session.summary}"
            },
        ]

        # thêm history gần nhất
        messages += session.history

        # câu hỏi mới
        messages.append({"role": "user", "content": data.msg})

        # ====================
        # GỌI GROQ
        # ====================
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7
        )

        reply_text = response.choices[0].message.content

        if reply_text is None:
            reply_text = "Mini hơi lag xíu… bạn thử lại nhé 😆"

        # ====================
        # CẬP NHẬT HISTORY
        # ====================
        session.history.append({"role": "user", "content": data.msg})
        session.history.append({"role": "assistant", "content": reply_text})

        # giữ tối đa 40 tin (20 lượt hỏi đáp)
        if len(session.history) > 40:
            session.history = session.history[-40:]

        # ====================
        # UPDATE SUMMARY
        # ====================
        summary_res = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Hãy tóm tắt nội dung hội thoại bằng tiếng Việt, tối đa 2 câu, "
                        "giữ đúng ý chính, không lan man."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Tóm tắt cũ: {session.summary}\n"
                        f"Lịch sử mới nhất: {session.history}"
                    )
                }
            ],
            temperature=0.2
        )

        new_summary = summary_res.choices[0].message.content
        if new_summary and len(new_summary) > 10:
            session.summary = new_summary

        return {
            "assistant": "Mini",
            "reply": reply_text,
            "summary": session.summary,
            "stored_messages": len(session.history)
        }

    except Exception as e:
        return {
            "assistant": "Mini",
            "reply": f"Mini bị lỗi xíu: {str(e)} 😭",
        }

