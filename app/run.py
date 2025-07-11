import os
from flask import Flask
from flask_login import LoginManager
from controllers import user_controller
from controllers import asistencia_controller
from controllers import reunion_controller
from controllers import duenio_controller
from controllers import terreno_controller
from database import db
from models.user_model import User

app = Flask(__name__)

# Define la ruta absoluta para la base de datos
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sistema.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "clave-secreta"

login_manager = LoginManager()
login_manager.login_view = "user.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)
app.register_blueprint(user_controller.user_bp)
app.register_blueprint(asistencia_controller.asistencia_bp)
app.register_blueprint(duenio_controller.duenio_bp)
app.register_blueprint(reunion_controller.reunion_bp)
app.register_blueprint(terreno_controller.terreno_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)