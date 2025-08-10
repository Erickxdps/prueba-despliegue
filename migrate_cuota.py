"""
Script de migración para agregar campos titulo y descripcion a la tabla Cuota
"""
import sqlite3
import os

def migrate_database():
    # Ruta a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'sistema.db')
    
    print(f"Conectando a la base de datos: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(Cuota)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Columnas actuales en Cuota: {columns}")
        
        # Agregar columna titulo si no existe
        if 'titulo' not in columns:
            print("Agregando columna 'titulo'...")
            cursor.execute("ALTER TABLE Cuota ADD COLUMN titulo TEXT DEFAULT 'Cuota sin título'")
            print("✅ Columna 'titulo' agregada exitosamente")
        else:
            print("ℹ️  Columna 'titulo' ya existe")
        
        # Agregar columna descripcion si no existe
        if 'descripcion' not in columns:
            print("Agregando columna 'descripcion'...")
            cursor.execute("ALTER TABLE Cuota ADD COLUMN descripcion TEXT")
            print("✅ Columna 'descripcion' agregada exitosamente")
        else:
            print("ℹ️  Columna 'descripcion' ya existe")
        
        # Actualizar registros existentes que tengan titulo como default
        cursor.execute("UPDATE Cuota SET titulo = 'Cuota general' WHERE titulo = 'Cuota sin título' OR titulo IS NULL")
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} registros actualizados con título por defecto")
        
        # Confirmar cambios
        conn.commit()
        print("✅ Migración completada exitosamente")
        
        # Mostrar estructura actualizada
        cursor.execute("PRAGMA table_info(Cuota)")
        columns_info = cursor.fetchall()
        print("\n📊 Estructura actualizada de la tabla Cuota:")
        for column in columns_info:
            print(f"  - {column[1]} ({column[2]}) {'NOT NULL' if column[3] else 'NULL'}")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    migrate_database()
    print("✨ Migración finalizada")
