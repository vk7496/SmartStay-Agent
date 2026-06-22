import anthropic
import json

client = anthropic.Anthropic()  # از ANTHROPIC_API_KEY در Streamlit Secrets میخونه

def extract_reservation_info(text: str) -> dict:
    """
    متن آزاد مسافر رو میگیره و شعبه + تعداد شب رو برمیگردونه.
    خروجی: {"شعبه": "تهران", "تعداد": 2}
    """
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""اطلاعات رزرو را از متن زیر استخراج کن. فقط JSON برگردان، هیچ توضیحی نده.
شعبه‌های معتبر: تهران، اصفهان، گیلان

متن: {text}

فرمت خروجی: {{"شعبه": "نام شعبه", "تعداد": عدد}}"""
        }]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
