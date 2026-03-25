import pandas as pd
import sqlite3

ruta = r'C:/daymler/Proyectos/MM/datos_excel/glosas.xlsx'
df = pd.read_excel(ruta)


# 2. Renombrar columnas
df = df.rename(columns={
    'ÍTEM': 'item_codigo',
    'PARTIDAS': 'glosa',
    'UNIDAD': 'unidad',
    'CANTIDAD': 'cantidad',
    'P. U ($)': 'precio_unitario',
    'P. TOTAL ($)': 'precio_total'
})

# 3. Eliminar filas sin código (importante)
df = df[df['item_codigo'].notna()]

# 4. Limpiar datos
df['item_codigo'] = df['item_codigo'].astype(str).str.strip()
df['glosa'] = df['glosa'].astype(str).str.strip()

# 5. Crear jerarquía
df['nivel'] = df['item_codigo'].str.count('\.') + 1

df['parent_id'] = df['item_codigo'].apply(
    lambda x: '.'.join(x.split('.')[:-1]) if '.' in x else None
)

# 6. Dejar estructura final
df_final = df[[
    'item_codigo',
    'glosa',
    'parent_id',
    'nivel',
    'unidad',
    'cantidad',
    'precio_unitario'
]]

# 7. Ver resultado
print(df_final.head(15))

# conectar a la base
conn = sqlite3.connect("presupuesto.db")

# insertar datos
df_final.to_sql('items', conn, if_exists='append', index=False)

# cerrar conexión
conn.close()

print("Datos cargados en SQLite 🚀")