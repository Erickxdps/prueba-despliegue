from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import login_required, current_user
from models.asistencia_model import Asistencia
from models.duenio_model import Duenio
from models.reunion_model import Reunion
from models.multa_model import Multa
from views import asistencia_view
from utils.decorators import role_required
from database import db
from sqlalchemy import or_  # Importar or_ para búsquedas
from controllers.multa_controller import es_dueno_inmune

asistencia_bp = Blueprint("asistencia", __name__)

# Ruta para obtener la lista de asistencias con paginación y búsqueda
@asistencia_bp.route("/asistencias")
@login_required
def list_asistencias():
    # Obtener parámetros de búsqueda y paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # 10 registros por página por defecto
    search = request.args.get('search', '', type=str)
    
    # Construir la consulta base con joins para búsqueda
    query = db.session.query(Asistencia).join(Duenio).join(Reunion)
    
    # Aplicar filtro de búsqueda si existe
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Duenio.nombre.ilike(search_filter),
                Duenio.paterno.ilike(search_filter),
                Duenio.materno.ilike(search_filter),
                Duenio.ci.ilike(search_filter),
                Reunion.titulo.ilike(search_filter),
                Reunion.descripcion.ilike(search_filter)
            )
        )
    
    # Aplicar paginación (ordenar por fecha de reunión descendente para mostrar las más recientes primero)
    asistencias_paginated = query.order_by(Reunion.fecha.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Calcular estadísticas globales (de todas las asistencias, no solo de la página actual)
    if search:
        # Si hay búsqueda, calcular estadísticas de los resultados filtrados
        total_query = query
    else:
        # Si no hay búsqueda, calcular estadísticas de todas las asistencias
        total_query = db.session.query(Asistencia).join(Duenio).join(Reunion)
    
    # Estadísticas globales
    total_asistencias = total_query.count()
    total_presentes = total_query.filter(Asistencia.asistio == True).count()
    total_ausentes = total_query.filter(Asistencia.asistio == False).count()
    reuniones_unicas = total_query.with_entities(Asistencia.id_reunion).distinct().count()
    
    return asistencia_view.list_asistencias(asistencias_paginated, search, {
        'total_asistencias': total_asistencias,
        'total_presentes': total_presentes,
        'total_ausentes': total_ausentes,
        'reuniones_unicas': reuniones_unicas
    })

# Ruta para crear asistencias (manual, raramente usada)
@asistencia_bp.route("/asistencias/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_asistencia():
    if request.method == "POST":
        if current_user.has_role("admin"):
            duenio_id = request.form["duenio_id"]
            id_reunion = request.form["id_reunion"]
            asistio = 'asistio' in request.form  # Procesar el checkbox
            
            # Verificar si ya existe una asistencia para este dueño y reunión
            asistencia_existente = Asistencia.query.filter_by(
                duenio_id=duenio_id, 
                id_reunion=id_reunion
            ).first()
            
            if asistencia_existente:
                # Actualizar asistencia existente
                asistencia_existente.update(asistio=asistio)
                reunion = Reunion.query.get(id_reunion)
                gestionar_multa_asistencia(asistencia_existente, asistio, reunion)
                
                if asistio:
                    flash("Asistencia actualizada: Presente. Multa eliminada.", "success")
                else:
                    flash("Asistencia actualizada: Ausente. Multa aplicada.", "warning")
            else:
                # Crear nueva asistencia
                asistencia = Asistencia(duenio_id=duenio_id, id_reunion=id_reunion, asistio=asistio)
                asistencia.save()
                
                # Obtener reunión para gestionar multas correctamente
                reunion = Reunion.query.get(id_reunion)
                
                # Gestionar multa según asistencia
                gestionar_multa_asistencia(asistencia, asistio, reunion)
                
                if asistio:
                    flash("Asistencia registrada: Presente. Sin multa.", "success")
                else:
                    flash("Asistencia registrada: Ausente. Multa aplicada.", "warning")
            
            return redirect(url_for("asistencia.list_asistencias"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    duenios = Duenio.query.all()
    reuniones = Reunion.query.all()
    return asistencia_view.create_asistencia(duenios, reuniones)

# Ruta para actualizar asistencias por ID
@asistencia_bp.route("/asistencias/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_asistencia(id):
    asistencia = Asistencia.query.get(id)
    if not asistencia:
        return "Asistencia no encontrada", 404
    
    if request.method == "POST":
        if current_user.has_role("admin"):
            # Manejar tanto checkbox HTML como valor JavaScript
            asistio_value = request.form.get("asistio")
            asistio = asistio_value in ['true', 'on', True] or 'asistio' in request.form
            
            # Actualizar asistencia
            asistencia.update(asistio=asistio)
            
            # Gestionar multa según asistencia
            reunion = Reunion.query.get(asistencia.id_reunion)
            gestionar_multa_asistencia(asistencia, asistio, reunion)
            
            flash("Asistencia actualizada exitosamente", "success")
            return redirect(url_for("asistencia.list_asistencias"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    return asistencia_view.update_asistencia(asistencia)

# Ruta para eliminar asistencias por ID
@asistencia_bp.route("/asistencias/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_asistencia(id):
    asistencia = Asistencia.get_by_id(id)
    if not asistencia:
        flash("Asistencia no encontrada", "error")
        return redirect(url_for("asistencia.list_asistencias"))
    
    if current_user.has_role("admin"):
        try:
            # Eliminar multa asociada antes de eliminar asistencia
            eliminar_multa_asistencia(asistencia)
            asistencia.delete()
            flash("Asistencia eliminada exitosamente", "success")
        except Exception as e:
            flash("Error al eliminar la asistencia", "error")
        return redirect(url_for("asistencia.list_asistencias"))
    else:
        return jsonify({"message": "Unauthorized"}), 403

# Ruta para marcar asistencia específica
@asistencia_bp.route("/asistencias/marcar", methods=["POST"])
@login_required
@role_required("admin")
def marcar_asistencia():
    duenio_id = request.form["duenio_id"]
    id_reunion = request.form["id_reunion"]
    asistio = request.form.get("asistio") == "true"
    
    asistencia = Asistencia.query.filter_by(duenio_id=duenio_id, id_reunion=id_reunion).first()
    if asistencia:
        asistencia.update(asistio=asistio)
        reunion = Reunion.query.get(asistencia.id_reunion)
        gestionar_multa_asistencia(asistencia, asistio, reunion)
        flash("Asistencia marcada exitosamente", "success")
    else:
        flash("Asistencia no encontrada", "error")
    
    return redirect(url_for("asistencia.list_asistencias"))

# Funciones auxiliares para gestión de multas
def crear_multa_asistencia(asistencia, monto_multa):
    """Crear multa para asistencia"""
    print(f"[DEBUG] Intentando crear multa - Dueño: {asistencia.duenio_id}, Reunión: {asistencia.id_reunion}, Monto: {monto_multa}")
    
    # 🛡️ VERIFICAR INMUNIDAD ETERNA
    if es_dueno_inmune(asistencia.duenio_id):
        print(f"🛡️ [INMUNIDAD] Dueño {asistencia.duenio_id} tiene inmunidad eterna - No se crea multa por asistencia")
        return
    
    multa_existente = Multa.query.filter_by(
        duenio_id=asistencia.duenio_id,
        reunion_id=asistencia.id_reunion,
        tipo='asistencia'
    ).first()
    
    if not multa_existente:
        try:
            multa = Multa(
                duenio_id=asistencia.duenio_id,
                reunion_id=asistencia.id_reunion,
                monto=monto_multa,
                tipo='asistencia',
                descripcion=f'Multa por no asistir a reunión {asistencia.id_reunion}'
            )
            multa.save()
            print(f"[DEBUG] Multa creada exitosamente - ID: {multa.multa_id}")
        except Exception as e:
            print(f"[ERROR] Error al crear multa: {e}")
            raise e
    else:
        print(f"[DEBUG] Ya existe multa para este dueño y reunión")

def gestionar_multa_asistencia(asistencia, asistio, reunion):
    """Gestionar multa según estado de asistencia"""
    print(f"[DEBUG] Gestionando multa - Dueño: {asistencia.duenio_id}, Asistió: {asistio}, Reunión: {reunion.id if reunion else 'None'}")
    
    multa = Multa.query.filter_by(
        duenio_id=asistencia.duenio_id,
        reunion_id=asistencia.id_reunion,
        tipo='asistencia'
    ).first()
    
    if asistio and multa:
        # Si asistió, eliminar multa
        print(f"[DEBUG] Asistió - Eliminando multa existente ID: {multa.multa_id}")
        multa.delete()
    elif not asistio and not multa and reunion and reunion.monto_multa > 0:
        # Si no asistió y no hay multa, crear multa
        print(f"[DEBUG] No asistió - Creando nueva multa")
        crear_multa_asistencia(asistencia, reunion.monto_multa)
    else:
        print(f"[DEBUG] Sin cambios - Asistió: {asistio}, Multa existe: {multa is not None}")

def eliminar_multa_asistencia(asistencia):
    """Eliminar multa asociada a asistencia"""
    multa = Multa.query.filter_by(
        duenio_id=asistencia.duenio_id,
        reunion_id=asistencia.id_reunion,
        tipo='asistencia'
    ).first()
    if multa:
        multa.delete()