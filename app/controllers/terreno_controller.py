from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template # type: ignore
from flask_login import login_required, current_user # type: ignore
from models.terreno_model import Terreno
from models.duenio_model import Duenio
from views import terreno_view
from utils.decorators import role_required
from database import db
from sqlalchemy import or_  # Importar or_ para búsquedas

terreno_bp = Blueprint("terreno", __name__)

# Ruta para obtener la lista de terrenos con paginación y búsqueda
@terreno_bp.route("/terrenos")
@login_required
def list_terrenos():
    # Obtener parámetros de búsqueda y paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # 10 registros por página por defecto
    search = request.args.get('search', '', type=str)
    
    # Construir la consulta base con join para búsqueda en dueño
    query = db.session.query(Terreno).join(Duenio)
    
    # Aplicar filtro de búsqueda si existe
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Terreno.lugar.ilike(search_filter),
                Terreno.manzano.ilike(search_filter),
                Duenio.nombre.ilike(search_filter),
                Duenio.paterno.ilike(search_filter),
                Duenio.materno.ilike(search_filter),
                Duenio.ci.ilike(search_filter)
            )
        )
    
    # Aplicar paginación
    terrenos_paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Calcular estadísticas globales (de todos los terrenos, no solo de la página actual)
    if search:
        # Si hay búsqueda, calcular estadísticas de los resultados filtrados
        total_query = query
    else:
        # Si no hay búsqueda, calcular estadísticas de todos los terrenos
        total_query = db.session.query(Terreno).join(Duenio)
    
    # Estadísticas globales
    total_terrenos = total_query.count()
    total_metros = total_query.with_entities(db.func.sum(Terreno.metros_cuadrados)).scalar() or 0
    manzanos_unicos = total_query.with_entities(Terreno.manzano).distinct().count()
    
    # Redondear los metros cuadrados para evitar decimales largos
    total_metros = round(float(total_metros), 2)
    
    return terreno_view.list_terrenos(terrenos_paginated, search, {
        'total_terrenos': total_terrenos,
        'total_metros': total_metros,
        'manzanos_unicos': manzanos_unicos
    })
     
# Ruta para crear terrenos
@terreno_bp.route("/terrenos/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_terreno():
    if request.method == "POST":
        if current_user.has_role("admin"):
            duenio_id = request.form["duenio_id"]
            lugar = request.form["lugar"]
            manzano = int(request.form["manzano"])
            metros_cuadrados = float(request.form["metros_cuadrados"])  # Cambiado a float
            terreno = Terreno(duenio_id=duenio_id, lugar=lugar, manzano=manzano, metros_cuadrados=metros_cuadrados)
            terreno.save()
            flash("Terreno creado exitosamente", "success")
            return redirect(url_for("terreno.list_terrenos"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    duenios = Duenio.query.all()
    return render_template('create_terreno.html', duenios=duenios)

# Ruta para actualizar terrenos por ID
@terreno_bp.route("/terrenos/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_terreno(id):
    terreno = Terreno.query.get(id)
    if not terreno:
        return "Terreno no encontrado", 404
    if request.method == "POST":
        if current_user.has_role("admin"):
            id_duenio = request.form["id_duenio"]
            lugar = request.form["lugar"]
            manzano = int(request.form["manzano"])
            metros_cuadrados = float(request.form["metros_cuadrados"])
            terreno.update(duenio_id=id_duenio, lugar=lugar, manzano=manzano, metros_cuadrados=metros_cuadrados)
            flash("Terreno actualizado exitosamente", "success")
            return redirect(url_for("terreno.list_terrenos"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    duenios = Duenio.query.all()
    return render_template('update_terreno.html', terreno=terreno, duenios=duenios)

# Ruta para eliminar terrenos por ID
@terreno_bp.route("/terrenos/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_terreno(id):
    terreno = Terreno.get_by_id(id)
    if not terreno:
        flash("Terreno no encontrado", "error")
        return redirect(url_for("terreno.list_terrenos"))
    if current_user.has_role("admin"):
        try:
            terreno.delete()
            flash("Terreno eliminado exitosamente", "success")
        except Exception as e:
            flash("Error al eliminar el terreno", "error")
        return redirect(url_for("terreno.list_terrenos"))
    else:
        return jsonify({"message": "Unauthorized"}), 403
