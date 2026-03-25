from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

# ruta robusta templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

DB_PATH = r"C:/daymler/Proyectos/MM/db/presupuesto.db"


# =========================
# FUNCIÓN ORDEN JERÁRQUICO
# =========================
def ordenar_codigo(codigo):
    try:
        return [int(x) for x in str(codigo).split('.')]
    except:
        return [999999]


# =========================
# GET DATA
# =========================
def get_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            item_codigo,
            glosa,
            unidad,
            cantidad,
            precio_unitario,
            cantidad * precio_unitario AS precio_total
        FROM items
    """)

    rows = cursor.fetchall()
    conn.close()

    # 🔥 ordenar correctamente en Python
    rows = sorted(rows, key=lambda x: ordenar_codigo(x[0]))

    return rows


# =========================
# ENDPOINT
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    data = get_data()

    return templates.TemplateResponse(
        "table.html",
        {
            "request": request,
            "data": data
        }
    )