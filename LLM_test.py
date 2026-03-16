from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # ← cette ligne DOIT être là avant os.getenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Explain deep learning in 2 sentences"}
    ]
)

print(response.choices[0].message.content)