import sqlite3

conn = sqlite3.connect("presupuesto.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_codigo TEXT NOT NULL,
    glosa TEXT,
    parent_id TEXT,
    nivel INTEGER,
    unidad TEXT,
    cantidad REAL,
    precio REAL
);
""")

conn.commit()
conn.close()

print("Tabla creada correctamente")