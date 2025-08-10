import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join('app', 'sistema.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Actualizar títulos vacíos
cursor.execute("UPDATE Cuota SET titulo = 'Cuota general' WHERE titulo IS NULL OR titulo = ''")
print(f"✅ {cursor.rowcount} registros actualizados")

conn.commit()
conn.close()
print("✅ Base de datos actualizada")
