import pdfplumber
import pandas as pd
import sqlite3
import json
import os
from openai import OpenAI

# =========================
# CONFIG
# =========================
PDF_PATH = r"C:\daymler\Proyectos\MM\datos_excel\glosas_pdf.pdf"
DB_PATH = r"C:\daymler\Proyectos\MM\db\presupuesto.db"

client = OpenAI()

# =========================
# 1. EXTRAER TEXTO DEL PDF
# =========================
def extraer_texto_pdf(ruta):
    texto = ""
    with pdfplumber.open(ruta) as pdf:
        for page in pdf.pages:
            contenido = page.extract_text()
            if contenido:
                texto += contenido + "\n"
    return texto


# =========================
# 2. CONSTRUIR PROMPT
# =========================
def construir_prompt(texto):
    return f"""
Tienes un presupuesto de construcción en texto.

Extrae una tabla con estas columnas:
- item_codigo
- glosa
- unidad
- cantidad
- precio_unitario

Reglas:
- Respeta jerarquía (ej: 1, 1.1, 1.1.1)
- Si no hay datos, usar null
- NO inventar valores
- Solo devolver JSON válido (lista de objetos)

Texto:
{texto[:12000]}
"""


# =========================
# 3. LLM → JSON
# =========================
def procesar_con_llm(texto):
    prompt = construir_prompt(texto)

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    salida = response.output_text

    try:
        data = json.loads(salida)
    except:
        print("⚠️ Error parseando JSON. Output:")
        print(salida)
        raise

    return data


# =========================
# 4. LIMPIEZA
# =========================
def limpiar_dataframe(df):

    # strip
    df['item_codigo'] = df['item_codigo'].astype(str).str.strip()
    df['glosa'] = df['glosa'].astype(str).str.strip()

    # jerarquía
    df['nivel'] = df['item_codigo'].str.count(r'\.') + 1

    df['parent_id'] = df['item_codigo'].apply(
    lambda x: '.'.join(str(x).split('.')[:-1]) if pd.notna(x) and '.' in str(x) else None
    )

    # numéricos
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')

    df['precio_unitario'] = (
        df['precio_unitario']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
    )

    df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce')

    return df


# =========================
# 5. GUARDAR EN SQLITE
# =========================
def guardar_sqlite(df, db_path):
    conn = sqlite3.connect(db_path)
    df.to_sql('items', conn, if_exists='replace', index=False)
    conn.close()


# =========================
# MAIN
# =========================
def main():

    print("📄 Extrayendo texto PDF...")
    texto = extraer_texto_pdf(PDF_PATH)

    print("🤖 Procesando con LLM...")
    data = procesar_con_llm(texto)

    print("📊 Convirtiendo a DataFrame...")
    df = pd.DataFrame(data)

    print("🧹 Limpiando datos...")
    df = limpiar_dataframe(df)

    print("💾 Guardando en SQLite...")
    guardar_sqlite(df, DB_PATH)

    print("✅ Listo. Datos cargados en:", os.path.abspath(DB_PATH))


if __name__ == "__main__":
    main()