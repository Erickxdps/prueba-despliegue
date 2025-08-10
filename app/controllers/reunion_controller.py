from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models.reunion_model import Reunion
from models.duenio_model import Duenio
from models.asistencia_model import Asistencia
from models.multa_model import Multa
from views import reunion_view
from utils.decorators import role_required
from database import db

reunion_bp = Blueprint("reunion", __name__)

# Ruta para obtener la lista de reuniones
@reunion_bp.route("/reuniones")
def list_reuniones():
    reuniones = Reunion.get_all()
    return reunion_view.list_reuniones(reuniones)

# Ruta para crear reuniones
@reunion_bp.route("/reuniones/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def create_reunion():
    if request.method == "POST":
        if current_user.has_role("admin"):
            fecha_str = request.form["fecha"]
            hora_str = request.form["hora"]
            descripcion = request.form.get("descripcion")
            monto_multa = float(request.form.get("monto_multa", 100.0))
            
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
            reunion = Reunion(fecha=fecha, hora=hora, descripcion=descripcion, monto_multa=monto_multa)
            reunion.save()

            # Crear asistencias y multas para todos los duenios
            duenios = Duenio.query.all()
            for duenio in duenios:
                # Crear asistencia con asistio=False por defecto
                asistencia = Asistencia(duenio_id=duenio.id, id_reunion=reunion.id)
                asistencia.save()
                
                # Crear multa usando el monto de la reunión (si > 0)
                if reunion.monto_multa > 0:
                    multa = Multa(
                        duenio_id=duenio.id,
                        reunion_id=reunion.id,
                        monto=reunion.monto_multa,  # Usar monto de la reunión
                        tipo='asistencia',
                        descripcion=f'Multa por no asistir a reunión {reunion.id}'
                    )
                    multa.save()
            
            flash("Reunión creada exitosamente", "success")
            return redirect(url_for("reunion.list_reuniones"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    return reunion_view.create_reunion()

# Ruta para actualizar reuniones por ID
@reunion_bp.route("/reuniones/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_reunion(id):
    reunion = Reunion.get_by_id(id)
    if not reunion:
        return "Reunión no encontrada", 404
    
    if request.method == "POST":
        if current_user.has_role("admin"):
            fecha_str = request.form.get("fecha")
            hora_str = request.form.get("hora")
            descripcion = request.form.get("descripcion")
            monto_multa = float(request.form.get("monto_multa", reunion.monto_multa))
            
            if fecha_str:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                reunion.update(fecha=fecha)
            if hora_str:
                hora = datetime.strptime(hora_str, "%H:%M").time()
                reunion.update(hora=hora)
            if descripcion is not None:
                reunion.update(descripcion=descripcion)
            if monto_multa is not None:
                reunion.update(monto_multa=monto_multa)
            
            flash("Reunión actualizada exitosamente", "success")
            return redirect(url_for("reunion.list_reuniones"))
        else:
            return jsonify({"message": "Unauthorized"}), 403
    
    return reunion_view.update_reunion(reunion)

# Ruta para eliminar reuniones por ID
@reunion_bp.route("/reuniones/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_reunion(id):
    reunion = Reunion.get_by_id(id)
    if not reunion:
        flash("Reunión no encontrada", "error")
        return redirect(url_for("reunion.list_reuniones"))
    
    if current_user.has_role("admin"):
        try:
            # Eliminar multas asociadas a esta reunión
            multas = Multa.query.filter_by(reunion_id=id).all()
            print(f"DEBUG: Encontradas {len(multas)} multas para eliminar con reunion_id={id}")
            for multa in multas:
                print(f"DEBUG: Eliminando multa ID={multa.multa_id}, duenio_id={multa.duenio_id}")
                db.session.delete(multa)
            
            # Eliminar asistencias asociadas
            asistencias = Asistencia.query.filter_by(id_reunion=id).all()
            print(f"DEBUG: Encontradas {len(asistencias)} asistencias para eliminar con id_reunion={id}")
            for asistencia in asistencias:
                print(f"DEBUG: Eliminando asistencia ID={asistencia.id}, duenio_id={asistencia.duenio_id}")
                db.session.delete(asistencia)
            
            # Eliminar reunión
            print(f"DEBUG: Eliminando reunión ID={reunion.id}")
            db.session.delete(reunion)
            
            # Confirmar todos los cambios
            db.session.commit()
            print(f"DEBUG: Reunión {id} y sus datos asociados eliminados exitosamente")
            
            flash("Reunión eliminada exitosamente", "success")
            return redirect(url_for("reunion.list_reuniones"))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error al eliminar reunión: {str(e)}")
            flash(f"Error al eliminar la reunión: {str(e)}", "error")
            return redirect(url_for("reunion.list_reuniones"))
    else:
        return jsonify({"message": "Unauthorized"}), 403