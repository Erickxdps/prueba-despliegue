"""
Script de prueba para verificar que las multas se están guardando correctamente
"""

# Para ejecutar este script desde la terminal de VS Code:
# python -c "
# import sys
# sys.path.append('app')
# from database import db
# from models.multa_model import Multa
# from models.duenio_model import Duenio
# from run import app

# with app.app_context():
#     print('=== VERIFICACIÓN DE MULTAS ===')
#     multas = Multa.query.all()
#     print(f'Total de multas en la base de datos: {len(multas)}')
#     
#     for multa in multas:
#         print(f'  - Multa #{multa.multa_id}: {multa.duenio.nombre} - Bs.{multa.monto} - {multa.tipo}')
#     
#     print('=== VERIFICACIÓN DE DUEÑOS ===')
#     duenios = Duenio.query.all()
#     print(f'Total de dueños: {len(duenios)}')
#     
#     for duenio in duenios:
#         multas_duenio = len(duenio.multas)
#         print(f'  - {duenio.nombre}: {multas_duenio} multas')
# "

print("Para verificar las multas, ejecuta el comando de arriba en la terminal")
print("O ve a http://127.0.0.1:5000/multas en el navegador")
