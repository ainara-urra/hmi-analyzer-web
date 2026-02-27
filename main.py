import os
import re
import base64
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sirve los archivos estáticos (HTML, CSS, JS, imágenes, iconos SVG)
app.mount("/static", StaticFiles(directory="static"), name="static")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BRIDGES = [
    ("PUENTE 01 – ORIENTAR", "Orientación del usuario y visibilidad del estado del sistema."),
    ("PUENTE 02 – ENFOCAR",  "Jerarquía visual y señal frente a ruido."),
    ("PUENTE 03 – ADVERTIR", "Claridad y prioridad de alertas y avisos."),
    ("PUENTE 04 – ENTENDER", "Relaciones causa–efecto y contexto operativo."),
    ("PUENTE 05 – PROYECTAR","Tendencias y anticipación del estado futuro."),
    ("PUENTE 06 – GUIAR",    "Secuencias guiadas y recuperación ante errores."),
    ("PUENTE 07 – ACCEDER",  "Ergonomía digital y accesibilidad de controles."),
    ("PUENTE 08 – APRENDER", "Uso del histórico y aprendizaje del operador."),
]


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    tipo_sistema: str = Form(...),
    nivel_criticidad: str = Form(...),
    perfil_usuario: str = Form(...),
    entorno_operativo: str = Form(...),
):
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Detectar tipo MIME
    ct = file.content_type or "image/jpeg"

    contexto = (
        f"Condiciones operativas:\n"
        f"- Tipo de sistema: {tipo_sistema}\n"
        f"- Nivel de criticidad: {nivel_criticidad}\n"
        f"- Perfil del usuario: {perfil_usuario}\n"
        f"- Entorno operativo: {entorno_operativo}"
    )

    scores = []
    bridge_results = []

    for title, criteria in BRIDGES:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un auditor UX industrial muy exigente. "
                        "Evalúas interfaces HMI comparándolas con estándares profesionales. "
                        "Utiliza una escala estricta y sé crítico."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Evalúa la interfaz HMI según {title}.\n\n"
                                f"{criteria}\n\n"
                                f"{contexto}\n\n"
                                "Instrucciones:\n"
                                "- Ajusta la exigencia según criticidad y entorno.\n"
                                "- Si el sistema es Seguridad o Emergencia, sé especialmente estricto.\n"
                                "- Si el entorno es Alta presión o Emergencia, penaliza ambigüedades.\n"
                                "- Si el usuario es nuevo, valora especialmente claridad y guiado.\n\n"
                                "Formato obligatorio:\n"
                                "PUNTUACIÓN: X/10\n"
                                "RESUMEN: una única frase clara basada en elementos visibles concretos "
                                "de la imagen. Evita frases genéricas."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{ct};base64,{image_base64}"},
                        },
                    ],
                },
            ],
        )

        content = response.choices[0].message.content
        score = None
        summary = ""

        match = re.search(r"(?<!\d)(\d{1,2})(?:\.\d+)?\s*/\s*10", content)
        if match:
            score = round(float(match.group(1)))

        for line in content.splitlines():
            if "RESUMEN" in line.upper():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    summary = parts[1].strip()

        if score is None:
            continue

        scores.append(score)
        bridge_results.append(
            {"title": title, "score": score, "summary": summary}
        )

    if not scores:
        return JSONResponse({"error": "No se pudieron calcular puntuaciones."}, status_code=500)

    average = round(sum(scores) / len(scores), 1)

    # Síntesis final
    global_inputs = [f"{r['title']}: {r['summary']}" for r in bridge_results]
    synthesis_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un experto en UX industrial que sintetiza evaluaciones "
                    "para público no experto de forma clara, crítica y directa."
                ),
            },
            {
                "role": "user",
                "content": (
                    "A partir de los siguientes resultados por puente:\n\n"
                    + "\n".join(global_inputs)
                    + "\n\nGenera un resumen FINAL con esta estructura exacta:\n\n"
                    "OBSERVACIONES CLAVE:\n"
                    "- bullet 1\n- bullet 2\n- bullet 3\n\n"
                    "IMPACTO OPERATIVO:\n"
                    "- bullet 1\n- bullet 2\n- bullet 3\n\n"
                    "OPORTUNIDADES DE MEJORA:\n"
                    "- bullet 1\n- bullet 2\n- bullet 3\n\n"
                    "Lenguaje claro, directo y no técnico. Máximo 3 bullets por sección."
                ),
            },
        ],
    )

    synthesis_text = synthesis_response.choices[0].message.content

    return JSONResponse(
        {
            "bridges": bridge_results,
            "average": average,
            "synthesis": synthesis_text,
        }
    )
