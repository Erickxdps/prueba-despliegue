#!/usr/bin/env python3
"""
Script para inicializar la base de datos con usuarios por defecto.
Crea un usuario normal y un administrador para facilitar el desarrollo.
"""

import os
import sys

# Agregar el directorio app al path de Python
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Cambiar al directorio de la aplicación
os.chdir(app_dir)

# Importar todo lo necesario
from database import db
from run import app
from models.user_model import User

def create_default_users():
    """Crear usuarios por defecto en la base de datos"""
    
    with app.app_context():
        try:
            # Verificar si ya existen usuarios
            existing_users = User.get_all()
            if existing_users:
                print(f"⚠️  Ya existen {len(existing_users)} usuarios en la base de datos:")
                for user in existing_users:
                    print(f"   - {user.username} ({user.role})")
                
                response = input("\n¿Deseas crear usuarios por defecto de todas formas? (s/n): ")
                if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                    print("❌ Operación cancelada")
                    return False
            
            print("🔄 Creando usuarios por defecto...")
            
            # 1. Usuario administrador por defecto
            admin_user = User.get_user_by_username("admin")
            if not admin_user:
                admin_user = User(
                    username="admin",
                    password="contra69882061",  # Contraseña personalizada
                    role="admin"
                )
                admin_user.save()
                print("✅ Usuario administrador creado:")
                print("   - Usuario: admin")
                print("   - Contraseña: contra69882061")
                print("   - Rol: admin")
            else:
                print("⚠️  Usuario 'admin' ya existe")
            
            # 2. Usuario doctor por defecto
            doctor_user = User.get_user_by_username("doctor")
            if not doctor_user:
                doctor_user = User(
                    username="doctor",
                    password="contra69882061",  # Contraseña personalizada
                    role="doctor"
                )
                doctor_user.save()
                print("✅ Usuario doctor creado:")
                print("   - Usuario: doctor")
                print("   - Contraseña: contra69882061")
                print("   - Rol: doctor")
            else:
                print("⚠️  Usuario 'doctor' ya existe")
            
            print()
            print("🎯 USUARIOS POR DEFECTO LISTOS:")
            print("📱 Para iniciar sesión como ADMINISTRADOR:")
            print("   Usuario: admin")
            print("   Contraseña: contra69882061")
            print()
            print("👤 Para iniciar sesión como USUARIO NORMAL:")
            print("   Usuario: doctor")
            print("   Contraseña: contra69882061")
            print()
            print("🔒 RECOMENDACIÓN DE SEGURIDAD:")
            print("   ⚠️  Cambia estas contraseñas por defecto en producción")
            print("   ⚠️  Estos usuarios son solo para desarrollo/pruebas")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al crear usuarios por defecto: {e}")
            return False

def initialize_database():
    """Inicializar la base de datos completa"""
    
    with app.app_context():
        try:
            print("🔄 Inicializando base de datos...")
            
            # Crear todas las tablas si no existen
            db.create_all()
            print("✅ Tablas de base de datos verificadas/creadas")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
            return False

if __name__ == "__main__":
    print("🚀 INICIALIZADOR DE BASE DE DATOS")
    print("=" * 50)
    
    # Inicializar base de datos
    if not initialize_database():
        print("❌ Error en la inicialización")
        sys.exit(1)
    
    # Crear usuarios por defecto
    if not create_default_users():
        print("❌ Error al crear usuarios")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("🔥 La aplicación está lista para usar con usuarios por defecto")
