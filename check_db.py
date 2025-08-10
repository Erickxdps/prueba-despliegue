import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join('app', 'sistema.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== VERIFICACIÓN DE LA BASE DE DATOS ===")

# Verificar usuarios
cursor.execute('SELECT COUNT(*) FROM user')
user_count = cursor.fetchone()[0]
print(f'\nTotal usuarios: {user_count}')

if user_count > 0:
    cursor.execute('SELECT user_id, username, email, role FROM user LIMIT 5')
    users = cursor.fetchall()
    print('Usuarios disponibles:')
    for user in users:
        print(f'  ID: {user[0]}, Usuario: {user[1]}, Email: {user[2]}, Rol: {user[3]}')

# Verificar cuotas
cursor.execute('SELECT COUNT(*) FROM cuota')
cuota_count = cursor.fetchone()[0]
print(f'\nTotal cuotas: {cuota_count}')

if cuota_count > 0:
    cursor.execute('SELECT cuota_id, titulo, monto, pagado FROM cuota')
    cuotas = cursor.fetchall()
    print('Cuotas disponibles:')
    for cuota in cuotas:
        print(f'  ID: {cuota[0]}, Título: {cuota[1]}, Monto: {cuota[2]}, Pagado: {cuota[3]}')

conn.close()
