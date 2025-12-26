from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

API_KEY = "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"
client = Groq(api_key=API_KEY)

app = FastAPI()

class Message(BaseModel):
    msg: str

# --- MEMORY ---
memory_summary = "Ngữ cảnh ban đầu: Người dùng nói chuyện tiếng Việt. Trợ lý trả lời tự nhiên, thân thiện."
recent_history = []   # chỉ lưu một số câu gần nhất


@app.post("/chat")
async def chat(data: Message):
    global memory_summary, recent_history

    try:
        # Chuẩn bị messages gửi cho model
        messages = [
            {"role": "system", "content": "Bạn là trợ lý AI tiếng Việt, trả lời tự nhiên, thân thiện, dễ hiểu."},
            {"role": "system", "content": f"Tóm tắt hội thoại trước đây: {memory_summary}"}
        ]

        # Thêm lịch sử gần nhất
        messages += recent_history

        # Thêm câu hỏi mới
        messages.append({"role": "user", "content": data.msg})

        # Gọi AI
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        reply_text = response.choices[0].message.content

        # --- Cập nhật recent history ---
        recent_history.append({"role": "user", "content": data.msg})
        recent_history.append({"role": "assistant", "content": reply_text})

        # chỉ giữ 10 dòng gần nhất (5 lượt hỏi đáp)
        if len(recent_history) > 10:
            recent_history = recent_history[-10:]

        # --- Cập nhật SUMMARY ---
        summary_update = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Hãy tóm tắt rất ngắn gọn nội dung hội thoại dưới đây bằng tiếng Việt (tối đa 2 câu), chỉ giữ ý chính."
                },
                {
                    "role": "user",
                    "content": f"Tóm tắt cũ: {memory_summary}\n"
                               f"Lịch sử gần đây: {recent_history}\n"
                               f"Trợ lý vừa trả lời: {reply_text}"
                }
            ]
        )

        memory_summary = summary_update.choices[0].message.content

        return {
            "reply": reply_text,
            "summary": memory_summary
        }

    except Exception as e:
        return {"reply": f"Lỗi server: {e}"}
