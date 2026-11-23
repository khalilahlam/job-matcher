import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT = """Analiza este CV y devuelve SOLO un JSON con esta estructura:
{
  "nombre": "",
  "puestos_objetivo": ["puestos a los que encaja, del más al menos probable"],
  "experiencia_anios": 0,
  "habilidades_fuertes": [],
  "habilidades_medias": [],
  "idiomas": {"idioma": "nivel"},
  "estudios": [],
  "ubicacion": "",
  "resumen": "2 frases sobre el perfil"
}
Reglas: no inventes nada que no esté en el CV. Si un dato no aparece, déjalo vacío."""

EXCLUIR = ("image", "tts", "audio", "live", "embedding", "robotics")


def modelos_disponibles() -> list[str]:
    """Modelos flash que tu clave puede usar, los 'lite' primero."""
    nombres = []
    try:
        for m in client.models.list():
            nombre = m.name.removeprefix("models/")
            acciones = getattr(m, "supported_actions", None) or []
            if "flash" in nombre and not any(x in nombre for x in EXCLUIR):
                if not acciones or "generateContent" in acciones:
                    nombres.append(nombre)
    except Exception as e:
        print(f"No pude listar modelos ({e}); uso el de por defecto.")
    nombres.sort(key=lambda n: ("lite" not in n, n))
    return nombres or ["gemini-3.8-flash"]


def extraer_perfil(ruta_pdf: str) -> dict:
    datos = Path(ruta_pdf).read_bytes()
    modelos = modelos_disponibles()
    print("Modelos a probar:", ", ".join(modelos))
    ultimo_error = None

    for modelo in modelos:
        for intento in range(2):
            try:
                print(f"Probando {modelo}...")
                respuesta = client.models.generate_content(
                    model=modelo,
                    contents=[
                        types.Part.from_bytes(data=datos, mime_type="application/pdf"),
                        PROMPT,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                return json.loads(respuesta.text)
            except Exception as e:
                ultimo_error = e
                texto = str(e)
                if "404" in texto:
                    break  # este modelo no sirve, pasa al siguiente
                if "503" in texto or "429" in texto:
                    if intento == 0:
                        print("  Ocupado, reintento en 10s...")
                        time.sleep(10)
                        continue
                    break  # sigue ocupado, pasa al siguiente modelo
                raise  # otro error (clave, PDF...): que salte

    raise RuntimeError(f"Ningún modelo respondió. Último error: {ultimo_error}")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "cv/mi_cv.pdf"
    perfil = extraer_perfil(ruta)
    Path("perfil.json").write_text(
        json.dumps(perfil, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(perfil, ensure_ascii=False, indent=2))