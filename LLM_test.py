from groq import Groq
import os

def test_groq_completion():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Explain deep learning in 2 sentences"}
        ]
    )

    assert response.choices[0].message.content is not None