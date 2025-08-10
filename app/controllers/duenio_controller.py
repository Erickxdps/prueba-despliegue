from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.duenio_model import Duenio
from models.multa_model import Multa  # Importar el modelo Multa
from views import duenio_view
from database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_  # Importar or_ para búsquedas
 
# Importamos el decorador de roles
from utils.decorators import role_required

duenio_bp = Blueprint("duenio", __name__)

# Ruta para obtener la lista de duenios con paginación y búsqueda
@duenio_bp.route("/duenios")
@login_required
def list_duenios():
    # Obtener parámetros de búsqueda y paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # 10 registros por página por defecto
    search = request.args.get('search', '', type=str)
    
    # Construir la consulta base
    query = Duenio.query
    
    # Aplicar filtro de búsqueda si existe
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Duenio.nombre.ilike(search_filter),
                Duenio.paterno.ilike(search_filter), 
                Duenio.materno.ilike(search_filter),
                Duenio.ci.ilike(search_filter)
            )
        )
    
    # Aplicar paginación
    duenios_paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return duenio_view.list_duenios(duenios_paginated, search)

# Ruta para crear duenios
@duenio_bp.route("/duenios/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_duenio():
    if request.method == "POST":
        if current_user.has_role("admin"):
            nombre = request.form["nombre"]
            paterno = request.form["paterno"]
            materno = request.form["materno"]
            ci = request.form["ci"]
            duenio = Duenio(nombre=nombre, paterno=paterno, materno=materno, ci=ci)
            try:
                duenio.save()
                # Crear una multa con monto 0 para el nuevo duenio
                # multa = Multa(duenio_id=duenio.id, monto=0)
                # multa.save()
                flash("Duenio creado exitosamente", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Error al crear el duenio", "error")
            return redirect(url_for("duenio.list_duenios"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    return duenio_view.create_duenio()

# Ruta para actualizar duenios por ID
@duenio_bp.route("/duenios/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_duenio(id):
    duenio = Duenio.get_by_id(id)
    if not duenio:
        return "Duenio no encontrado", 404
    if request.method == "POST":
        if current_user.has_role("admin"):
            nombre = request.form["nombre"]
            paterno = request.form["paterno"]
            materno = request.form["materno"]
            ci = request.form["ci"]
            duenio.update(nombre=nombre, paterno=paterno, materno=materno, ci=ci)
            flash("Duenio actualizado exitosamente", "success")
            return redirect(url_for("duenio.list_duenios"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    return duenio_view.update_duenio(duenio)

# Ruta para eliminar duenios por ID
@duenio_bp.route("/duenios/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_duenio(id):
    duenio = Duenio.get_by_id(id)
    if not duenio:
        flash("Duenio no encontrado", "error")
        return redirect(url_for("duenio.list_duenios"))
    if current_user.has_role("admin"):
        try:
            duenio.delete()
            flash("Duenio eliminado exitosamente", "success")
        except Exception as e:
            flash("Error al eliminar el duenio", "error")
        return redirect(url_for("duenio.list_duenios"))
    else:
        return jsonify({"message": "Unauthorized"}), 403