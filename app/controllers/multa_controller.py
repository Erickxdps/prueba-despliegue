from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template
from flask_login import login_required, current_user
from models.multa_model import Multa
from models.duenio_model import Duenio
from views import multa_view
from utils.decorators import role_required

multa_bp = Blueprint("multa", __name__)

# Ruta para obtener la lista de multas
@multa_bp.route("/multas")
@login_required
def list_multas():
    multas = Multa.get_all()
    return multa_view.list_multas(multas)

# Ruta para crear multas manualmente
@multa_bp.route("/multas/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_multa():
    if request.method == "POST":
        if current_user.has_role("admin"):
            duenio_id = request.form["duenio_id"]
            monto = float(request.form["monto"])
            tipo = request.form["tipo"]
            descripcion = request.form.get("descripcion", "")
            
            multa = Multa(
                duenio_id=duenio_id,
                monto=monto,
                tipo=tipo,
                descripcion=descripcion
            )
            multa.save()
            
            flash("Multa creada exitosamente", "success")
            return redirect(url_for("multa.list_multas"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    duenios = Duenio.query.all()
    return render_template('create_multa.html', duenios=duenios)

# Ruta para actualizar multas por ID
@multa_bp.route("/multas/<int:multa_id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_multa(multa_id):
    multa = Multa.get_by_id(multa_id)
    if not multa:
        return "Multa no encontrada", 404
    
    if request.method == "POST":
        if current_user.has_role("admin"):
            duenio_id = request.form.get("duenio_id", multa.duenio_id)
            monto = float(request.form.get("monto", multa.monto))
            tipo = request.form.get("tipo", multa.tipo)
            descripcion = request.form.get("descripcion", multa.descripcion)
            
            multa.update(
                duenio_id=duenio_id,
                monto=monto,
                tipo=tipo,
                descripcion=descripcion
            )
            
            flash("Multa actualizada exitosamente", "success")
            return redirect(url_for("multa.list_multas"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    duenios = Duenio.query.all()
    return render_template('update_multa.html', multa=multa, duenios=duenios)

# Ruta para eliminar multas por ID
@multa_bp.route("/multas/<int:multa_id>/delete")
@login_required
@role_required("admin")
def delete_multa(multa_id):
    multa = Multa.get_by_id(multa_id)
    if not multa:
        return "Multa no encontrada", 404
    
    if current_user.has_role("admin"):
        multa.delete()
        flash("Multa eliminada exitosamente", "success")
        return redirect(url_for("multa.list_multas"))
    else:
        return jsonify({"message": "Unauthorized"}), 403

# Ruta para ver multas por duenio
@multa_bp.route("/multas/duenio/<int:duenio_id>")
@login_required
def multas_por_duenio(duenio_id):
    multas = Multa.get_by_duenio(duenio_id)
    duenio = Duenio.query.get(duenio_id)
    return multa_view.multas_por_duenio(multas, duenio)

# Ruta para ver multas por tipo
@multa_bp.route("/multas/tipo/<tipo>")
@login_required
def multas_por_tipo(tipo):
    if tipo not in ['cuota', 'asistencia']:
        return "Tipo de multa inválido", 400
    
    multas = Multa.get_by_tipo(tipo)
    return multa_view.multas_por_tipo(multas, tipo)

# Ruta para eliminar todas las multas de un duenio (cuando paga)
@multa_bp.route("/multas/duenio/<int:duenio_id>/eliminar_todas", methods=["POST"])
@login_required
@role_required("admin")
def eliminar_multas_duenio(duenio_id):
    multas = Multa.get_by_duenio(duenio_id)
    for multa in multas:
        multa.delete()
    
    flash(f"Todas las multas del duenio eliminadas exitosamente", "success")
    return redirect(url_for("multa.list_multas"))