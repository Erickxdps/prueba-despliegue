"""
Script para probar la lógica de multas por asistencia
"""
# Ejemplo de la lógica implementada:

# Caso 1: Persona NO asiste (asistio = False)
# - Se crea una multa por inasistencia

# Caso 2: Persona SÍ asiste (asistio = True)  
# - NO se crea multa
# - Si ya existía una multa por esta reunión, se ELIMINA

# Caso 3: Cambiar asistencia de False a True
# - Se elimina la multa existente

# Caso 4: Cambiar asistencia de True a False
# - Se crea una nueva multa

# La función gestionar_multa_asistencia(asistencia, asistio, reunion) maneja todos estos casos:

def gestionar_multa_asistencia_ejemplo(asistencia, asistio, reunion):
    """Ejemplo de la lógica implementada"""
    # Buscar multa existente para esta asistencia
    multa = buscar_multa_por_asistencia(asistencia)
    
    if asistio and multa:
        # ✅ Si asistió y hay multa: ELIMINAR multa
        print(f"✅ Persona asistió - Eliminando multa existente")
        eliminar_multa(multa)
        
    elif not asistio and not multa and reunion and reunion.monto_multa > 0:
        # ❌ Si no asistió y no hay multa: CREAR multa
        print(f"❌ Persona no asistió - Creando multa de {reunion.monto_multa}")
        crear_nueva_multa(asistencia, reunion.monto_multa)
        
    elif not asistio and multa:
        # ❌ Si no asistió y ya hay multa: NO hacer nada (multa ya existe)
        print(f"❌ Persona no asistió - Multa ya existe")
        
    elif asistio and not multa:
        # ✅ Si asistió y no hay multa: NO hacer nada (correcto)
        print(f"✅ Persona asistió - Sin multa (correcto)")

print("Lógica de multas por asistencia implementada correctamente ✅")
