from flask import Blueprint, request, redirect, url_for, flash, jsonify, render_template # type: ignore
from flask_login import login_required, current_user # type: ignore
from models.terreno_model import Terreno
from models.duenio_model import Duenio
from views import terreno_view
from utils.decorators import role_required

terreno_bp = Blueprint("terreno", __name__)

# Ruta para obtener la lista de terrenos
@terreno_bp.route("/terrenos")
@login_required
def list_terrenos():
    terrenos = Terreno.get_all()
    return terreno_view.list_terrenos(terrenos)
     
# Ruta para crear terrenos
@terreno_bp.route("/terrenos/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_terreno():
    if request.method == "POST":
        if current_user.has_role("admin"):
            dueño_id = request.form["dueño_id"]
            lugar = request.form["lugar"]
            manzano = int(request.form["manzano"])
            metros_cuadrados = float(request.form["metros_cuadrados"])  # Cambiado a float
            terreno = Terreno(dueño_id=dueño_id, lugar=lugar, manzano=manzano, metros_cuadrados=metros_cuadrados)
            terreno.save()
            flash("Terreno creado exitosamente", "success")
            return redirect(url_for("terreno.list_terrenos"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    dueños = Duenio.query.all()
    return render_template('create_terreno.html', dueños=dueños)

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
            terreno.update(dueño_id=id_duenio, lugar=lugar, manzano=manzano, metros_cuadrados=metros_cuadrados)
            flash("Terreno actualizado exitosamente", "success")
            return redirect(url_for("terreno.list_terrenos"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    dueños = Duenio.query.all()
    return render_template('update_terreno.html', terreno=terreno, dueños=dueños)

# Ruta para eliminar terrenos por ID
@terreno_bp.route("/terrenos/<int:id>/delete")
@login_required
@role_required("admin")
def delete_terreno(id):
    terreno = Terreno.get_by_id(id)
    if not terreno:
        return "Terreno no encontrado", 404
    if current_user.has_role("admin"):
        terreno.delete()
        flash("Terreno eliminado exitosamente", "success")
        return redirect(url_for("terreno.list_terrenos"))
    else:
        return jsonify({"message": "Unauthorized"}), 403
