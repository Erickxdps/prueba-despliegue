#!/usr/bin/env python3
"""
Script para recrear la base de datos con las configuraciones CASCADE actualizadas.
Este script hará una copia de seguridad de los datos y recreará las tablas.
"""

import os
import sys
import shutil
from datetime import datetime

# Agregar el directorio de la aplicación al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Importar desde el directorio app
from database import db

# Importar la aplicación Flask configurada
sys.path.append('app')
from run import app

def backup_database():
    """Crear copia de seguridad de la base de datos actual"""
    db_path = 'app/sistema.db'
    if os.path.exists(db_path):
        backup_name = f'sistema_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2(db_path, backup_name)
        print(f"✅ Copia de seguridad creada: {backup_name}")
        return True
    else:
        print("⚠️  No se encontró la base de datos existente")
        return False

def recreate_database():
    """Recrear la base de datos con las nuevas configuraciones CASCADE"""
    try:
        with app.app_context():
            # Eliminar todas las tablas
            db.drop_all()
            print("✅ Tablas existentes eliminadas")
            
            # Recrear todas las tablas con las nuevas configuraciones
            db.create_all()
            print("✅ Nuevas tablas creadas con configuraciones CASCADE")
            
        return True
    except Exception as e:
        print(f"❌ Error al recrear la base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Iniciando migración de base de datos...")
    
    # Crear copia de seguridad
    backup_success = backup_database()
    
    # Recrear base de datos
    if recreate_database():
        print("✅ Migración completada exitosamente")
        print("📝 Nota: Las configuraciones CASCADE ahora permiten eliminar dueños y terrenos con registros relacionados")
        print("⚠️  Recuerda: Todos los datos existentes se han perdido. Deberás volver a crear los registros.")
    else:
        print("❌ Error en la migración")
        if backup_success:
            print("💡 Puedes restaurar la base de datos desde el backup si es necesario")
