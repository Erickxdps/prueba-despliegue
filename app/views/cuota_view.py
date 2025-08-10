from flask import render_template
from flask_login import current_user


# La función `list_cuotas` recibe una lista de
# cuotaes y renderiza el template `cuotaes.html`
def list_cuotas(cuotas, cuotas_por_propietario=None, cuotas_por_titulo=None):
    return render_template(
        "cuotas.html",
        cuotas = cuotas,
        cuotas_por_propietario = cuotas_por_propietario,
        cuotas_por_titulo = cuotas_por_titulo,
        title="Lista de cuotas",
        current_user=current_user,
    )


# La función `create_cuota` renderiza el
# template `create_cuota.html` o devuelve un JSON
# según la solicitud
def create_cuota(terrenos=None):
    from models.terreno_model import Terreno
    if terrenos is None:
        terrenos = Terreno.query.all()
    return render_template(
        "create_cuota.html", 
        title="Crear Cuota", 
        terrenos=terrenos,
        current_user=current_user
    )


# La función `update_cuota` recibe un cuota
# y renderiza el template `update_cuota.html`
def update_cuota(cuota, terrenos=None):
    from models.terreno_model import Terreno
    if terrenos is None:
        terrenos = Terreno.query.all()
    return render_template(
        "update_cuota.html",
        title="Editar Cuota",
        cuota=cuota,
        terrenos=terrenos,
        current_user=current_user,
    )
