from flask import render_template
from flask_login import current_user


# La función `list_duenios` recibe un objeto paginado de
# duenios y renderiza el template `duenios.html` 
def list_duenios(duenios_paginated, search=""):
    return render_template(
        "duenios.html",
        duenios_paginated=duenios_paginated,
        duenios=duenios_paginated.items,  # Mantener compatibilidad
        search=search,
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
