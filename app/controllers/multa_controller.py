from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import login_required, current_user
from models.multa_model import Multa
from models.duenio_model import Duenio
from models.reunion_model import Reunion
from sqlalchemy.exc import IntegrityError  # Importar IntegrityError
from database import db

# Importamos el decorador de roles
from utils.decorators import role_required

multa_bp = Blueprint("multa", __name__)

# Ruta para obtener la lista de multas
@multa_bp.route("/multas")
def list_multas():
    multas = Multa.get_all()
    dueños = Duenio.get_all()
    reuniones = Reunion.get_all()
    return render_template('multas.html', multas=multas, dueños=dueños, reuniones=reuniones)

# Ruta para crear multas
@multa_bp.route("/multas/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_multa():
    if request.method == "POST":
        if current_user.has_role("admin"):
            dueño_id = request.form.get("dueño_id")
            id_reunion = request.form.get("id_reunion")
            monto = request.form.get("monto", 100)
            multa = Multa(dueño_id=dueño_id, id_reunion=id_reunion, monto=monto)
            try:
                multa.save()
                flash("Multa creada exitosamente", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Error al crear la multa", "error")
            return redirect(url_for("multa.list_multas"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    dueños = Duenio.query.all()
    reuniones = Reunion.query.all()
    return render_template('create_multa.html', dueños=dueños, reuniones=reuniones)

# Ruta para actualizar multas por ID
@multa_bp.route("/multas/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_multa(id):
    multa = Multa.get_by_id(id)
    if not multa:
        return "Multa no encontrada", 404
    if request.method == "POST":
        if current_user.has_role("admin"):
            dueño_id = request.form["dueño_id"]
            id_reunion = request.form["id_reunion"]
            monto = request.form["monto"]
            multa.dueño_id = dueño_id
            multa.id_reunion = id_reunion
            multa.monto = monto
            db.session.commit()
            flash("Multa actualizada exitosamente", "success")
            return redirect(url_for("multa.list_multas"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    dueños = Duenio.query.all()
    reuniones = Reunion.query.all()
    return render_template('update_multa.html', multa=multa, dueños=dueños, reuniones=reuniones)

# Ruta para eliminar multas por ID
@multa_bp.route("/multas/<int:id>/delete")
@login_required
@role_required("admin")
def delete_multa(id):
    multa = Multa.get_by_id(id)
    if not multa:
        return "Multa no encontrada", 404
    if current_user.has_role("admin"):
        db.session.delete(multa)
        db.session.commit()
        flash("Multa eliminada exitosamente", "success")
        return redirect(url_for("multa.list_multas"))
    else:
        return jsonify({"message": "Unauthorized"}), 403