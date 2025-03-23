from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models.reunion_model import Reunion
from views import reunion_view
from utils.decorators import role_required

reunion_bp = Blueprint("reunion", __name__)

# Ruta para obtener la lista de reuniones
@reunion_bp.route("/reuniones")
def list_reuniones():
    reuniones = Reunion.get_all()
    return reunion_view.list_reuniones(reuniones)

@reunion_bp.route("/reuniones/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_reunion():
    if request.method == "POST":
        if current_user.has_role("admin"):
            fecha_str = request.form["fecha"]
            hora_str = request.form["hora"]
            descripcion = request.form.get("descripcion")
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
            reunion = Reunion(fecha=fecha, hora=hora, descripcion=descripcion)
            reunion.save()
            flash("Reunión creada exitosamente", "success")
            return redirect(url_for("reunion.list_reuniones"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    return reunion_view.create_reunion()

@reunion_bp.route("/reuniones/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_reunion(id):
    reunion = Reunion.get_by_id(id)
    if not reunion:
        return "Reunión no encontrada", 404
    if request.method == "POST":
        if current_user.has_role("admin"):
            fecha_str = request.form["fecha"]
            hora_str = request.form["hora"]
            descripcion = request.form.get("descripcion")
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M:%S").time() 
            reunion.update(fecha=fecha, hora=hora, descripcion=descripcion)
            flash("Reunión actualizada exitosamente", "success")
            return redirect(url_for("reunion.list_reuniones"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    return reunion_view.update_reunion(reunion)

@reunion_bp.route("/reuniones/<int:id>/delete")
@login_required
@role_required("admin")
def delete_reunion(id):
    reunion = Reunion.get_by_id(id)
    if not reunion:
        return "Reunión no encontrada", 404
    if current_user.has_role("admin"):
        reunion.delete()
        flash("Reunión eliminada exitosamente", "success")
        return redirect(url_for("reunion.list_reuniones"))
    else:
        return jsonify({"message": "Unauthorized"}), 403