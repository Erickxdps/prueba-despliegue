#!/usr/bin/env python3
"""
Script para recrear las tablas con CASCADE desde la aplicación Flask.
"""

import os
import sys

# Cambiar al directorio de la aplicación
os.chdir(os.path.join(os.path.dirname(__file__), 'app'))

# Importar todo lo necesario
from database import db
from run import app

def recreate_tables():
    """Recrear solo las tablas con problemas de CASCADE"""
    try:
        with app.app_context():
            print("🔄 Iniciando recreación de tablas...")
            
            # Solo recrear las tablas problemáticas manteniendo los datos posibles
            from models.terreno_model import Terreno
            from models.asistencia_model import Asistencia
            
            # Eliminar las tablas problemáticas
            db.session.execute(db.text('PRAGMA foreign_keys = OFF'))
            
            # Recrear todas las tablas para asegurar integridad
            db.drop_all()
            db.create_all()
            
            # Reactivar foreign keys
            db.session.execute(db.text('PRAGMA foreign_keys = ON'))
            db.session.commit()
            
            print("✅ Tablas recreadas con configuraciones CASCADE")
            print("📝 Nota: La base de datos está lista para eliminaciones en cascada")
            print("⚠️  Los datos existentes se han perdido - deberás recrear los registros")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    recreate_tables()
