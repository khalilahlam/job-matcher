import json
import time

from google.genai import types

from cv_a_perfil import client, modelos_disponibles

PROMPT = """Eres un asistente que evalúa ofertas de empleo para un candidato concreto.

PERFIL DEL CANDIDATO:
{perfil}

OFERTA:
{oferta}

Responde SOLO con un JSON válido con esta estructura:
{{
  "titulo": "puesto de la oferta",
  "empresa": "nombre o vacío si no aparece",
  "puntuacion": 0,
  "descartada": false,
  "motivo_descarte": "solo si choca con un no negociable, un sector descartado o el sueldo mínimo",
  "cumple": ["requisitos que el candidato cumple"],
  "faltan": ["requisitos que no cumple"],
  "no_indicado": ["datos que la oferta no menciona: sueldo, modalidad..."],
  "resumen": "2 frases sobre el encaje"
}}

Reglas:
- No inventes datos que la oferta no menciona; anótalos en "no_indicado".
- Si la oferta no indica sueldo, modalidad o tipo de contrato, no descartes por ello; anótalo en "no_indicado".
- Marca "descartada": true solo cuando haya un choque claro con un sector descartado, una condición no negociable o un sueldo explícito inferior al mínimo del candidato.
- Sé exigente: más de 90 solo si encaja casi todo.
- Si la oferta pide mucha más experiencia de la que tiene el candidato, baja la puntuación."""


def _a_lista_str(valor) -> list[str]:
    if isinstance(valor, list):
        return [str(x).strip() for x in valor if str(x).strip()]
    if isinstance(valor, str) and valor.strip():
        return [x.strip() for x in valor.split(",") if x.strip()]
    return []


def normalizar_evaluacion(data: dict) -> dict:
    if not isinstance(data, dict):
        data = {}
    try:
        puntuacion = int(float(data.get("puntuacion", 0)))
    except Exception:
        puntuacion = 0
    puntuacion = max(0, min(100, puntuacion))

    descartada = bool(data.get("descartada", False))
    motivo = str(data.get("motivo_descarte") or "").strip()
    if not descartada:
        motivo = ""

    return {
        "titulo": str(data.get("titulo") or "Oferta sin título").strip(),
        "empresa": str(data.get("empresa") or "Empresa no indicada").strip(),
        "puntuacion": puntuacion,
        "descartada": descartada,
        "motivo_descarte": motivo,
        "cumple": _a_lista_str(data.get("cumple")),
        "faltan": _a_lista_str(data.get("faltan")),
        "no_indicado": _a_lista_str(data.get("no_indicado")),
        "resumen": str(data.get("resumen") or "").strip(),
    }


def puntuar_oferta(perfil: dict, texto: str) -> dict:
    contenido = PROMPT.format(
        perfil=json.dumps(perfil, ensure_ascii=False),
        oferta=texto[:8000],
    )
    ultimo = None
    for modelo in modelos_disponibles():
        for intento in range(2):
            try:
                r = client.models.generate_content(
                    model=modelo,
                    contents=contenido,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                parsed = json.loads(r.text)
                return normalizar_evaluacion(parsed)
            except Exception as e:
                ultimo = e
                t = str(e)
                if "404" in t:
                    break
                if "503" in t or "429" in t:
                    if intento == 0:
                        time.sleep(8)
                        continue
                    break
                raise
    raise RuntimeError(f"Ningún modelo respondió. Último error: {ultimo}")