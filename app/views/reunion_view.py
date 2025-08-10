from flask import render_template
from flask_login import current_user
from datetime import datetime, date


# La función `list_reuniones` recibe una lista de
# reuniones y renderiza el template `reuniones.html`
def list_reuniones(reuniones):
    return render_template(
        "reuniones.html",
        reuniones = reuniones,
        title="Lista de reuniones",
        current_user=current_user,
        today=date.today(),
    )


# La función `create_reunion` renderiza el
# template `create_reunion.html` o devuelve un JSON
# según la solicitud
def create_reunion():
    return render_template(
        "create_reunion.html", title="Crear Libro", current_user=current_user
    )


# La función `update_reunion` recibe un reunion
# y renderiza el template `update_reunion.html`
def update_reunion(reunion):
    return render_template(
        "update_reunion.html",
        title="Editar Libro",
        reunion=reunion,
        current_user=current_user,
    )
