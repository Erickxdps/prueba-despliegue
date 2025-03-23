from flask import render_template
from flask_login import current_user


# La función `list_asistencias` recibe una lista de
# asistenciaes y renderiza el template `asistenciaes.html`
def list_asistencias(asistencias):
    return render_template(
        "asistencias.html",
        asistencias = asistencias,
        title="Lista de asistencias",
        current_user=current_user,
    )


# La función `create_asistencia` renderiza el
# template `create_asistencia.html` o devuelve un JSON
# según la solicitud
def create_asistencia():
    return render_template(
        "create_asistencia.html", title="Crear Libro", current_user=current_user
    )


# La función `update_asistencia` recibe un asistencia
# y renderiza el template `update_asistencia.html`
def update_asistencia(asistencia):
    return render_template(
        "update_asistencia.html",
        title="Editar Libro",
        asistencia=asistencia,
        current_user=current_user,
    )
