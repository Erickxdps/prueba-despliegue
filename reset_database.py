#!/usr/bin/env python3
"""
Script para RECREAR completamente la base de datos con usuarios por defecto.
⚠️ CUIDADO: Este script ELIMINARÁ todos los datos existentes.
"""

import os
import sys

# Agregar el directorio app al path de Python
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Cambiar al directorio de la aplicación
os.chdir(app_dir)

from database import db
from run import app
from models.user_model import User

def recreate_database_with_defaults():
    """Recrear completamente la base de datos con usuarios por defecto"""
    
    print("⚠️  ADVERTENCIA: Este proceso eliminará TODOS los datos existentes")
    response = input("¿Estás seguro de que quieres continuar? (escribir 'SI' para confirmar): ")
    
    if response != 'SI':
        print("❌ Operación cancelada")
        return False
    
    with app.app_context():
        try:
            print("🔄 Eliminando todas las tablas...")
            db.drop_all()
            
            print("🔄 Recreando todas las tablas...")
            db.create_all()
            
            print("🔄 Creando usuarios por defecto...")
            
            # Usuario administrador
            admin_user = User(
                username="admin",
                password="contra69882061",
                role="admin"
            )
            admin_user.save()
            
            # Usuario doctor
            doctor_user = User(
                username="doctor", 
                password="contra69882061",
                role="doctor"
            )
            doctor_user.save()
            
            print("✅ Base de datos recreada exitosamente")
            print()
            print("🎯 USUARIOS CREADOS:")
            print("👤 Administrador: admin / contra69882061")
            print("👤 Doctor: doctor / contra69882061")
            print()
            print("🚀 Base de datos lista para usar")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    print("🗂️ RECREADOR DE BASE DE DATOS")
    print("=" * 50)
    
    if recreate_database_with_defaults():
        print("=" * 50)
        print("✅ PROCESO COMPLETADO")
    else:
        print("=" * 50)
        print("❌ PROCESO FALLIDO")
        sys.exit(1)
