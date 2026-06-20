import ollama

def extract_reservation_info(text):
    prompt = f"""
    متن زیر درخواست رزرو یک مسافر برای هاستل است. اطلاعات را استخراج کن و فقط به صورت JSON برگردان:
    {text}
    فرمت خروجی: {{"شعبه": "نام شعبه", "تعداد": عدد}}
    """
    response = ollama.chat(model='qwen2.5:7b', messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']
