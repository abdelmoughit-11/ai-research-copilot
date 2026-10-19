from unittest.mock import patch
from groq import Groq
import os

@patch("groq.resources.chat.completions.Completions.create")
def test_groq_completion(mock_create):
    # On simule un objet de réponse renvoyé par l'API
    mock_response = mock_create.return_value
    mock_response.choices = [
        type("obj", (object,), {"message": type("obj", (object,), {"content": "Deep learning is a subset of machine learning using neural networks. It enables computers to learn from vast amounts of data."})})()
    ]

    client = Groq(api_key="fake-key-for-ci-testing")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Explain deep learning in 2 sentences"}
        ]
    )
#lola
    # On vérifie que le contenu simulé est bien récupéré
    assert response.choices[0].message.content is not None