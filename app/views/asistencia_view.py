from flask import render_template
from flask_login import current_user


# La función `list_asistencias` recibe una lista de
# asistenciaes y renderiza el template `asistenciaes.html`
def list_asistencias(asistencias, duenios=None, reuniones=None):
    from models.duenio_model import Duenio
    from models.reunion_model import Reunion
    
    # Si no se pasan duenios y reuniones, obtenerlos
    if duenios is None:
        duenios = Duenio.query.all()
    if reuniones is None:
        reuniones = Reunion.query.all()
        
    return render_template(
        "asistencias.html",
        asistencias=asistencias,
        duenios=duenios,
        reuniones=reuniones,
        title="Lista de asistencias",
        current_user=current_user,
    )


# La función `create_asistencia` renderiza el
# template `create_asistencia.html` o devuelve un JSON
# según la solicitud
def create_asistencia(duenios=None, reuniones=None):
    return render_template(
        "create_asistencia.html", 
        title="Crear Asistencia", 
        duenios=duenios,
        reuniones=reuniones,
        current_user=current_user
    )


# La función `update_asistencia` recibe un asistencia
# y renderiza el template `update_asistencia.html`
def update_asistencia(asistencia):
    from models.duenio_model import Duenio
    from models.reunion_model import Reunion
    
    duenios = Duenio.query.all()
    reuniones = Reunion.query.all()
    
    return render_template(
        "update_asistencia.html",
        title="Editar Asistencia",
        asistencia=asistencia,
        duenios=duenios,
        reuniones=reuniones,
        current_user=current_user,
    )
