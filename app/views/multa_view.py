from flask import render_template
from flask_login import current_user


# La función `list_multas` recibe una lista de
# multaes y renderiza el template `multaes.html`
def list_multas(multas):
    return render_template(
        "multas.html",
        multas = multas,
        title="Lista de multas",
        current_user=current_user,
    )


# La función `create_multa` renderiza el
# template `create_multa.html` o devuelve un JSON
# según la solicitud
def create_multa():
    return render_template(
        "create_multa.html", title="Crear Propietario", current_user=current_user
    )


# La función `update_multa` recibe un multa
# y renderiza el template `update_multa.html`
def update_multa(multa):
    return render_template(
        "update_multa.html",
        title="Editar Propietario",
        multa=multa,
        current_user=current_user,
    )
