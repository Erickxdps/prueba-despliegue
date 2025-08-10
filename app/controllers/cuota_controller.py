from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import login_required, current_user
from models.cuota_model import Cuota
from models.terreno_model import Terreno
from models.multa_model import Multa
from views import cuota_view
from utils.decorators import role_required
from database import db

cuota_bp = Blueprint("cuota", __name__)

# Ruta para obtener la lista de cuotas
@cuota_bp.route("/cuotas")
@login_required
def list_cuotas():
    cuotas = Cuota.get_all()
    print(f"DEBUG: Total cuotas encontradas: {len(cuotas)}")
    
    # Agrupar cuotas por tipo/título (esto es lo que realmente queremos mostrar)
    cuotas_por_tipo = {}
    for cuota in cuotas:
        titulo = cuota.titulo
        
        if titulo not in cuotas_por_tipo:
            cuotas_por_tipo[titulo] = {
                'titulo': titulo,
                'descripcion': cuota.descripcion,
                'monto_individual': cuota.monto,
                'cuotas_individuales': [],
                'propietarios_afectados': set(),
                'total_cuotas': 0,
                'cuotas_pagadas': 0,
                'cuotas_pendientes': 0,
                'monto_total': 0,
                'monto_pagado': 0,
                'monto_pendiente': 0,
                'fecha_creacion': cuota.fecha_creacion
            }
        
        # Agregar la cuota individual al grupo
        cuotas_por_tipo[titulo]['cuotas_individuales'].append(cuota)
        cuotas_por_tipo[titulo]['total_cuotas'] += 1
        cuotas_por_tipo[titulo]['monto_total'] += cuota.monto
        
        # Contar estados
        if cuota.pagado:
            cuotas_por_tipo[titulo]['cuotas_pagadas'] += 1
            cuotas_por_tipo[titulo]['monto_pagado'] += cuota.monto
        else:
            cuotas_por_tipo[titulo]['cuotas_pendientes'] += 1
            cuotas_por_tipo[titulo]['monto_pendiente'] += cuota.monto
        
        # Agregar propietario afectado
        if cuota.terreno and cuota.terreno.dueno:
            dueno = cuota.terreno.dueno
            nombre_completo = f"{dueno.nombre} {dueno.paterno} {dueno.materno}".strip()
            cuotas_por_tipo[titulo]['propietarios_afectados'].add(nombre_completo)
    
    # Convertir sets a listas para el template
    for titulo in cuotas_por_tipo:
        cuotas_por_tipo[titulo]['propietarios_afectados'] = list(cuotas_por_tipo[titulo]['propietarios_afectados'])
        cuotas_por_tipo[titulo]['num_propietarios'] = len(cuotas_por_tipo[titulo]['propietarios_afectados'])
    
    print(f"DEBUG: Tipos de cuotas encontrados: {list(cuotas_por_tipo.keys())}")
    print(f"DEBUG: Total tipos únicos: {len(cuotas_por_tipo)}")
    
    return cuota_view.list_cuotas(cuotas, cuotas_por_tipo)

# Ruta para crear cuotas
@cuota_bp.route("/cuotas/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_cuota():
    if request.method == "POST":
        if current_user.has_role("admin"):
            titulo = request.form["titulo"]
            descripcion = request.form.get("descripcion", "")
            monto = float(request.form["monto"])
            
            # Obtener todos los terrenos
            terrenos = Terreno.query.all()
            cuotas_creadas = 0
            
            # Crear una cuota para cada terreno
            for terreno in terrenos:
                cuota = Cuota(
                    terreno_id=terreno.id, 
                    titulo=titulo, 
                    monto=monto, 
                    descripcion=descripcion
                )
                
                # Agregar a la sesión y hacer flush para obtener el cuota_id
                db.session.add(cuota)
                db.session.flush()  # Esto asigna el cuota_id sin hacer commit
                
                # Ahora podemos crear la multa con el cuota_id disponible
                crear_multa_cuota(cuota)
                cuotas_creadas += 1
            
            # Hacer commit al final para todas las operaciones
            db.session.commit()
            
            flash(f"¡Cuota creada exitosamente! Se aplicó a {cuotas_creadas} terrenos.", "success")
            return redirect(url_for("cuota.list_cuotas"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    terrenos = Terreno.query.all()
    return cuota_view.create_cuota(terrenos)

# Ruta para actualizar cuotas por ID
@cuota_bp.route("/cuotas/<int:cuota_id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_cuota(cuota_id):
    cuota = Cuota.get_by_id(cuota_id)
    if not cuota:
        flash("Cuota no encontrada", "error")
        return redirect(url_for("cuota.list_cuotas"))

    if request.method == "POST":
        if current_user.has_role("admin"):
            titulo = request.form["titulo"]
            descripcion = request.form.get("descripcion", "")
            terreno_id = request.form["terreno_id"]
            monto = float(request.form["monto"])
            pagado = request.form.get("pagado") == "on"
            
            # Actualizar cuota
            cuota.update(
                titulo=titulo,
                descripcion=descripcion,
                terreno_id=terreno_id, 
                monto=monto, 
                pagado=pagado
            )
            
            # Gestionar multa según estado de pago
            gestionar_multa_cuota(cuota, pagado)
            
            flash("Cuota actualizada exitosamente", "success")
            return redirect(url_for("cuota.list_cuotas"))
        else:
            return jsonify({"message": "Unauthorized"}), 403

    terrenos = Terreno.query.all()
    return cuota_view.update_cuota(cuota, terrenos)

# Ruta para eliminar cuotas por ID
@cuota_bp.route("/cuotas/<int:cuota_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_cuota(cuota_id):
    cuota = Cuota.get_by_id(cuota_id)
    if cuota:
        # Eliminar multa asociada antes de eliminar cuota
        eliminar_multa_cuota(cuota)
        cuota.delete()
        flash("Cuota eliminada exitosamente", "success")
    else:
        flash("Cuota no encontrada", "error")
    
    return redirect(url_for("cuota.list_cuotas"))

# Ruta para cambiar estado de pago de una cuota (AJAX)
@cuota_bp.route("/cuotas/<int:cuota_id>/toggle-payment", methods=["POST"])
@login_required
@role_required("admin")
def toggle_payment(cuota_id):
    cuota = Cuota.get_by_id(cuota_id)
    if not cuota:
        return jsonify({"success": False, "message": "Cuota no encontrada"}), 404
    
    # Cambiar estado de pago
    new_pagado = not cuota.pagado
    cuota.update(pagado=new_pagado)
    
    # Gestionar multa según estado de pago
    gestionar_multa_cuota(cuota, new_pagado)
    
    return jsonify({
        "success": True, 
        "message": f"Cuota marcada como {'pagada' if new_pagado else 'pendiente'}",
        "pagado": new_pagado
    })

# Ruta para marcar como pagado
@cuota_bp.route("/cuotas/<int:cuota_id>/pagar", methods=["POST"])
@login_required
@role_required("admin")
def pagar_cuota(cuota_id):
    cuota = Cuota.get_by_id(cuota_id)
    if cuota:
        cuota.update(pagado=True)
        # Eliminar multa al marcar como pagado
        eliminar_multa_cuota(cuota)
        flash("Cuota marcada como pagada", "success")
    else:
        flash("Cuota no encontrada", "error")
    
    return redirect(url_for("cuota.list_cuotas"))

# Ruta para ver cuotas pendientes
@cuota_bp.route("/cuotas/pendientes")
@login_required
def cuotas_pendientes():
    cuotas = Cuota.get_pendientes()
    return cuota_view.list_cuotas_pendientes(cuotas)

# Funciones auxiliares para gestión de multas
def crear_multa_cuota(cuota):
    """Crear multa para cuota"""
    terreno = Terreno.query.get(cuota.terreno_id)
    if terreno:
        multa = Multa(
            duenio_id=terreno.duenio_id,
            cuota_id=cuota.cuota_id,  # Usar cuota_id que es la clave primaria
            monto=cuota.monto,
            tipo='cuota',
            descripcion=f'Cuota no pagada: {cuota.titulo}'
        )
        multa.save()

def gestionar_multa_cuota(cuota, pagado):
    """Gestionar multa según estado de pago"""
    multa = Multa.query.filter_by(cuota_id=cuota.cuota_id, tipo='cuota').first()
    
    if pagado and multa:
        # Si se pagó, eliminar multa
        multa.delete()
    elif not pagado and not multa:
        # Si no se pagó y no hay multa, crear multa
        crear_multa_cuota(cuota)

def eliminar_multa_cuota(cuota):
    """Eliminar multa asociada a cuota"""
    multa = Multa.query.filter_by(cuota_id=cuota.cuota_id, tipo='cuota').first()
    if multa:
        multa.delete()

# Ruta para eliminar todas las cuotas de un propietario específico
@cuota_bp.route("/cuotas/delete-by-owner/<int:dueno_id>", methods=["POST"])
@login_required
@role_required('admin')
def delete_cuotas_by_owner(dueno_id):
    try:
        # Obtener todas las cuotas del propietario a través de sus terrenos
        terrenos = Terreno.query.filter_by(id_dueno=dueno_id).all()
        total_eliminadas = 0
        
        for terreno in terrenos:
            cuotas = Cuota.query.filter_by(id_terreno=terreno.terreno_id).all()
            for cuota in cuotas:
                # Eliminar multas asociadas
                eliminar_multa_cuota(cuota)
                # Eliminar la cuota
                cuota.delete()
                total_eliminadas += 1
        
        flash(f"Se eliminaron {total_eliminadas} cuotas exitosamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar las cuotas: {str(e)}", "error")
    
    return redirect(url_for("cuota.list_cuotas"))

# Ruta para cambiar el estado de pago de una cuota (toggle)
@cuota_bp.route("/cuotas/<int:cuota_id>/toggle-status", methods=["POST"])
@login_required
@role_required('admin')
def toggle_cuota_status(cuota_id):
    try:
        cuota = Cuota.get_by_id(cuota_id)
        if not cuota:
            return jsonify({"success": False, "message": "Cuota no encontrada"}), 404
        
        data = request.get_json()
        nuevo_estado = data.get('pagado', False)
        
        cuota.update(pagado=nuevo_estado)
        
        mensaje = "pagada" if nuevo_estado else "marcada como pendiente"
        return jsonify({
            "success": True, 
            "message": f"Cuota {mensaje} exitosamente",
            "nuevo_estado": nuevo_estado
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# Ruta para eliminar una cuota específica
@cuota_bp.route("/cuotas/<int:cuota_id>", methods=["DELETE"])
@login_required
@role_required('admin')
def delete_cuota_single(cuota_id):
    try:
        cuota = Cuota.get_by_id(cuota_id)
        if not cuota:
            return jsonify({"success": False, "message": "Cuota no encontrada"}), 404
        
        titulo = cuota.titulo
        
        # Eliminar multas asociadas si existen
        try:
            eliminar_multa_cuota(cuota)
        except:
            pass  # Si no hay multa asociada, continuar
        
        # Eliminar la cuota
        cuota.delete()
        
        return jsonify({
            "success": True, 
            "message": f"Cuota '{titulo}' eliminada exitosamente"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# Ruta para eliminar todas las cuotas por título (todas las cuotas de un tipo específico)
@cuota_bp.route("/cuotas/delete-by-title/<string:titulo>", methods=["POST"])
@login_required
@role_required('admin')
def delete_cuotas_by_title(titulo):
    try:
        # Obtener todas las cuotas con el título específico
        cuotas = Cuota.query.filter_by(titulo=titulo).all()
        total_eliminadas = len(cuotas)
        afectados = set()
        
        for cuota in cuotas:
            # Registrar propietarios afectados
            if cuota.terreno and cuota.terreno.dueno:
                dueno_nombre = f"{cuota.terreno.dueno.nombre} {cuota.terreno.dueno.paterno or ''} {cuota.terreno.dueno.materno or ''}".strip()
                afectados.add(dueno_nombre)
            
            # Eliminar multas asociadas
            eliminar_multa_cuota(cuota)
            # Eliminar la cuota
            cuota.delete()
        
        propietarios_afectados = len(afectados)
        flash(f"Se eliminaron {total_eliminadas} cuotas del tipo '{titulo}' que afectaban a {propietarios_afectados} propietarios.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar las cuotas por título: {str(e)}", "error")
    
    return redirect(url_for("cuota.list_cuotas"))