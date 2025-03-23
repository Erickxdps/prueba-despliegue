from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import login_required, current_user
from models.asistencia_model import Asistencia
from models.duenio_model import Duenio
from models.reunion_model import Reunion
from models.terreno_model import Terreno
from models.multa_model import Multa  # Importar el modelo Multa
from sqlalchemy.exc import IntegrityError  # Importar IntegrityError
from views import asistencia_view
from database import db

# Importamos el decorador de roles
from utils.decorators import role_required

asistencia_bp = Blueprint("asistencia", __name__)


# Ruta para obtener la lista de asistencias
@asistencia_bp.route("/asistencias")
def list_asistencias():
    asistencias = Asistencia.get_all()
    dueños = Duenio.get_all()
    reuniones = Reunion.get_all()
    terrenos=Terreno.get_all()
    return render_template('asistencias.html', asistencias=asistencias, dueños=dueños, reuniones=reuniones,terrenos=terrenos)

# Ruta para crear asistencias
@asistencia_bp.route("/asistencias/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_asistencia():
    if request.method == "POST":
        if current_user.has_role("admin"):
            dueño_id = request.form.get("dueño_id")
            id_reunion = request.form.get("id_reunion")
            asistio = request.form.get("asistio")
            if asistio == "on":
                asistio = True
            else:
                asistio = False
            asistencia = Asistencia(dueño_id=dueño_id, id_reunion=id_reunion, asistio=asistio)
            try:
                asistencia.save()
                flash("Asistencia creada exitosamente", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Ya existe una asistencia para esta reunión y dueño", "error")
            return redirect(url_for("asistencia.list_asistencias"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    dueños = Duenio.query.all()
    reuniones = Reunion.query.all()
    return render_template('create_asistencia.html', dueños=dueños, reuniones=reuniones)

# Ruta para actualizar asistencias por ID
@asistencia_bp.route("/asistencias/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_asistencia(id):
    asistencia = Asistencia.get_by_id(id)
    if not asistencia:
        return "Asistencia no encontrada", 404
    if request.method == "POST":
        if current_user.has_role("admin"):
            dueño_id = request.form["dueño_id"]
            id_reunion = request.form["id_reunion"]
            asistio = request.form.get("asistio") == 'on'
            asistencia.update(dueño_id=dueño_id, id_reunion=id_reunion, asistio=asistio)
            flash("Asistencia actualizada exitosamente", "success")
            return redirect(url_for("asistencia.list_asistencias"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    dueños = Duenio.query.all()
    reuniones = Reunion.query.all()
    return render_template('update_asistencia.html', asistencia=asistencia, dueños=dueños, reuniones=reuniones)

# Ruta para eliminar asistencias por ID
@asistencia_bp.route("/asistencias/<int:id>/delete")
@login_required
@role_required("admin")
def delete_asistencia(id):
    asistencia = Asistencia.get_by_id(id)
    if not asistencia:
        return "Asistencia no encontrada", 404
    if current_user.has_role("admin"):
        asistencia.delete()
        flash("Asistencia eliminada exitosamente", "success")
        return redirect(url_for("asistencia.list_asistencias"))
    else:
        return jsonify({"message": "Unauthorized"}), 403