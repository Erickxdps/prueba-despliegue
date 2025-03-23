from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.duenio_model import Duenio
from models.multa_model import Multa  # Importar el modelo Multa
from views import duenio_view
from database import db
from sqlalchemy.exc import IntegrityError 
 
# Importamos el decorador de roles
from utils.decorators import role_required

duenio_bp = Blueprint("duenio", __name__)

# Ruta para obtener la lista de duenios
@duenio_bp.route("/duenios")
@login_required
def list_duenios():
    duenios = Duenio.get_all()
    return duenio_view.list_duenios(duenios)

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
                # Crear una multa con monto 0 para el nuevo dueño
                multa = Multa(dueño_id=duenio.id, monto=0)
                multa.save()
                flash("Dueño creado exitosamente", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Error al crear el dueño", "error")
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
        return "Dueño no encontrado", 404
    if request.method == "POST":
        if current_user.has_role("admin"):
            nombre = request.form["nombre"]
            paterno = request.form["paterno"]
            materno = request.form["materno"]
            ci = request.form["ci"]
            duenio.update(nombre=nombre, paterno=paterno, materno=materno, ci=ci)
            flash("Dueño actualizado exitosamente", "success")
            return redirect(url_for("duenio.list_duenios"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    return duenio_view.update_duenio(duenio)

# Ruta para eliminar duenios por ID
@duenio_bp.route("/duenios/<int:id>/delete")
@login_required
@role_required("admin")
def delete_duenio(id):
    duenio = Duenio.get_by_id(id)
    if not duenio:
        return "Dueño no encontrado", 404
    if current_user.has_role("admin"):
        duenio.delete()
        flash("Dueño eliminado exitosamente", "success")
        return redirect(url_for("duenio.list_duenios"))
    else:
        return jsonify({"message": "Unauthorized"}), 403