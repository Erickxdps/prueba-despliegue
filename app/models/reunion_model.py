from database import db
from datetime import date, time
from models.duenio_model import Duenio
from models.asistencia_model import Asistencia
from models.multa_model import Multa  # Importar el modelo Multa

class Reunion(db.Model):
    __tablename__ = "Reuniones"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)  # Nuevo campo

    def __init__(self, fecha, hora, descripcion=None):
        self.fecha = fecha
        self.hora = hora
        self.descripcion = descripcion

    def save(self):
        db.session.add(self)
        db.session.commit()
        # Crear registros de asistencia para todos los dueños
        dueños = Duenio.query.all()
        for dueño in dueños:
            asistencia = Asistencia(dueño_id=dueño.id, id_reunion=self.id, asistio=True)
            asistencia.save()

    @staticmethod
    def get_all():
        return Reunion.query.all()

    @staticmethod
    def get_by_id(id):
        return Reunion.query.get(id)

    def update(self, fecha=None, hora=None, descripcion=None):
        if fecha is not None:
            self.fecha = fecha
        if hora is not None:
            self.hora = hora
        if descripcion is not None:
            self.descripcion = descripcion
        db.session.commit()

    def delete(self):
        # Eliminar todas las asistencias y multas asociadas a esta reunión
        Asistencia.query.filter_by(id_reunion=self.id).delete()
        Multa.query.filter_by(id_reunion=self.id).delete()
        db.session.delete(self)
        db.session.commit()