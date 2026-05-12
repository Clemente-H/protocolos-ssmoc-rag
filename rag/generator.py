import os

from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """\
Eres un asistente médico especializado en protocolos y guías clínicas del sistema de salud chileno.

Tu trabajo es responder preguntas de médicos sobre derivaciones, contrarreferencias y protocolos clínicos.

Reglas:
- Responde en español.
- Sé directo y concreto. Los médicos no tienen tiempo.
- Siempre cita la fuente original: nombre del protocolo, página y enlace.
- Si la información no está en los documentos proporcionados, dilo claramente.
- No inventes información clínica.
"""


def generate_answer(query: str, context_chunks: list[dict]) -> str:
    """Call Mistral with the query and retrieved context to generate an answer with citations."""
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += (
            f"[[FUENTE {i}]]\n"
            f"Protocolo: {chunk['source_file']}\n"
            f"Página: {chunk['page']}\n"
            f"URL: {chunk['original_url']}\n"
            f"Texto:\n{chunk['text']}\n\n"
        )

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Pregunta: {query}\n\nFragmentos encontrados:\n\n{context_text}"},
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return response.choices[0].message.content
