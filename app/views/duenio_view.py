from flask import render_template
from flask_login import current_user


# La función `list_duenios` recibe una lista de
# duenioes y renderiza el template `duenioes.html`
def list_duenios(duenios):
    return render_template(
        "duenios.html",
        duenios = duenios,
        title="Lista de duenios",
        current_user=current_user,
    )


# La función `create_duenio` renderiza el
# template `create_duenio.html` o devuelve un JSON
# según la solicitud
def create_duenio():
    return render_template(
        "create_duenio.html", title="Crear Propietario", current_user=current_user
    )


# La función `update_duenio` recibe un duenio
# y renderiza el template `update_duenio.html`
def update_duenio(duenio):
    return render_template(
        "update_duenio.html",
        title="Editar Propietario",
        duenio=duenio,
        current_user=current_user,
    )
