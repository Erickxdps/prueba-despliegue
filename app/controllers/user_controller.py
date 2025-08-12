from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from utils.decorators import role_required
from views import user_view
from models.user_model import User
from models.asistencia_model import Asistencia
from models.terreno_model import Terreno
from models.duenio_model import Duenio
from models.reunion_model import Reunion
from models.cuota_model import Cuota
from models.multa_model import Multa

user_bp = Blueprint("user", __name__)

@user_bp.route('/')
def index():
    # Obtener conteos para las estadísticas (súper rápido)
    duenos_count = Duenio.query.count()
    terrenos_count = Terreno.query.count()
    reuniones_count = Reunion.query.count()
    
    # Para cuotas, contar solo tipos únicos de cuotas (no repetir por propietario)
    cuotas_titulos = Cuota.query.with_entities(Cuota.titulo).distinct().all()
    cuotas_count = len(cuotas_titulos)
    
    # Cargar solo primeros registros para el directorio (paginado)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # Solo 10 por defecto
    search = request.args.get('search', '', type=str)
    
    # Consulta optimizada con paginación para dueños únicos
    query = Duenio.query
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Duenio.nombre.ilike(search_filter)) |
            (Duenio.paterno.ilike(search_filter)) |
            (Duenio.materno.ilike(search_filter)) |
            (Duenio.ci.ilike(search_filter))
        )
    
    duenos_paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Función para multas (optimizada)
    def multas(multas_list):
        return sum(multa.monto for multa in multas_list)
    
    return render_template('index.html', 
                         duenos_count=duenos_count,
                         terrenos_count=terrenos_count, 
                         reuniones_count=reuniones_count,
                         cuotas_count=cuotas_count,
                         duenos_paginated=duenos_paginated,
                         search=search,
                         multas=multas)

# lista usuarios
@user_bp.route("/users")
@login_required
def list_users():
    users = User.get_all()
    return user_view.usuarios(users)

# logea a los usuarios por su usuario y su contra
@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Inicio de sesión exitoso", "success")
            if user.has_role("admin"):
                return redirect(url_for("user.list_users"))
            else:
                return redirect(url_for("user.profile", id=user.id))
        else:
            flash("Nombre de usuario o contrasenia incorrectos", "error")
    return user_view.login()

# cierra sesion
@user_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("user.login"))

# crea usuarios
@user_bp.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("El nombre de usuario ya está en uso", "error")
            return redirect(url_for("user.create_user"))
        user = User(username, password, role=role)
        user.save()
        flash("Usuario registrado exitosamente", "success")
        return redirect(url_for("user.list_users"))
    return user_view.registro()

# actualiza usuarios por ID
@user_bp.route("/users/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def update_user(id):
    user = User.get_by_id(id)
    if not user:
        return "Usuario no encontrado", 404
    if request.method == "POST":
        user.update()
        return redirect(url_for("user.list_users"))
    return user_view.actualizar(user)

# Elimina usuario por ID
@user_bp.route("/users/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(id):
    user = User.get_by_id(id)
    if not user:
        flash("Usuario no encontrado", "error")
        return redirect(url_for("user.list_users"))
    try:
        user.delete()
        flash("Usuario eliminado exitosamente", "success")
    except Exception as e:
        flash("Error al eliminar el usuario", "error")
    return redirect(url_for("user.list_users"))

# muestra el perfil
@user_bp.route("/profile/<int:id>")
@login_required
def profile(id):
    user = User.get_by_id(id)
    return user_view.perfil(user)

# ========== ENDPOINTS AJAX PARA MODALES ==========
@user_bp.route('/api/dueno/<int:dueno_id>/asistencias')
def get_dueno_asistencias(dueno_id):
    """Obtiene las asistencias de un dueño para el modal"""
    try:

        
        # Primero verificar que el dueño existe
        dueno = Duenio.query.get(dueno_id)
        if not dueno:
            print(f"ERROR: Dueño {dueno_id} no encontrado")
            return jsonify({'success': False, 'error': f'Dueño {dueno_id} no encontrado'}), 404
        

        
        # Buscar asistencias
        asistencias = Asistencia.query.filter_by(duenio_id=dueno_id).all()

        
        # Buscar multas por asistencia para este dueño
        multas_asistencia = Multa.query.filter_by(duenio_id=dueno_id, tipo='asistencia').all()

        
        # Crear diccionario de multas por reunión
        multas_por_reunion = {}
        for multa in multas_asistencia:
            multas_por_reunion[multa.reunion_id] = float(multa.monto)
        
        data = []
        for i, asistencia in enumerate(asistencias):

            try:
                # Verificar que la relación reunion existe
                if not asistencia.reunion:
                    print(f"WARNING: Asistencia {i+1} no tiene reunión asociada")
                    continue
                    
                reunion_data = {
                    'tema': asistencia.reunion.descripcion or 'Sin descripción',
                    'fecha': asistencia.reunion.fecha.strftime('%d/%m/%Y') if asistencia.reunion.fecha else 'Sin fecha',
                    'hora': asistencia.reunion.hora.strftime('%H:%M') if asistencia.reunion.hora else 'Sin hora'
                }
                
                # Buscar multa para esta reunión si no asistió
                multa_monto = 0
                if not asistencia.asistio and asistencia.id_reunion in multas_por_reunion:
                    multa_monto = multas_por_reunion[asistencia.id_reunion]

                
                asistencia_data = {
                    'reunion': reunion_data,
                    'presente': asistencia.asistio,
                    'multa_monto': multa_monto,
                    'observaciones': 'Sin observaciones'
                }
                data.append(asistencia_data)

                
            except Exception as e:
                print(f"ERROR al procesar asistencia {i+1}: {str(e)}")
                continue
        
        result = {
            'success': True,
            'dueno': {
                'nombre': f"{dueno.nombre} {dueno.paterno or ''} {dueno.materno or ''}",
                'ci': dueno.ci
            },
            'asistencias': data
        }
        

        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/api/dueno/<int:dueno_id>/terrenos')
def get_dueno_terrenos(dueno_id):
    """Obtiene los terrenos de un dueño para el modal"""
    try:

        
        dueno = Duenio.query.get(dueno_id)
        if not dueno:
            return jsonify({'success': False, 'error': f'Dueño {dueno_id} no encontrado'}), 404
        

        
        terrenos = Terreno.query.filter_by(duenio_id=dueno_id).all()

        
        data = []
        for terreno in terrenos:
            data.append({
                'numero_lote': terreno.lugar,
                'superficie': terreno.metros_cuadrados,
                'ubicacion': f"Manzana {terreno.manzano}",
                'descripcion': 'Sin descripción'
            })
        
        return jsonify({
            'success': True,
            'dueno': {
                'nombre': f"{dueno.nombre} {dueno.paterno or ''} {dueno.materno or ''}",
                'ci': dueno.ci
            },
            'terrenos': data
        })
    except Exception as e:
        print(f"ERROR TERRENOS: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/api/dueno/<int:dueno_id>/cuotas')
def get_dueno_cuotas(dueno_id):
    """Obtiene las cuotas de un dueño para el modal"""
    try:

        
        dueno = Duenio.query.get(dueno_id)
        if not dueno:
            return jsonify({'success': False, 'error': f'Dueño {dueno_id} no encontrado'}), 404
        

        
        # Buscar cuotas a través de terrenos
        cuotas = Cuota.query.join(Terreno).filter(Terreno.duenio_id == dueno_id).all()

        
        data = []
        for cuota in cuotas:
            monto = float(cuota.monto)
                
            data.append({
                'mes': 'N/A',
                'anio': 'N/A',
                'monto': monto,
                'estado': 'pagado' if cuota.pagado else 'pendiente',
                'descripcion': cuota.titulo,
                'fecha_vencimiento': cuota.fecha_creacion.strftime('%d/%m/%Y') if cuota.fecha_creacion else 'Sin fecha'
            })
        
        return jsonify({
            'success': True,
            'dueno': {
                'nombre': f"{dueno.nombre} {dueno.paterno or ''} {dueno.materno or ''}",
                'ci': dueno.ci
            },
            'cuotas': data
        })
    except Exception as e:
        print(f"ERROR CUOTAS: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
