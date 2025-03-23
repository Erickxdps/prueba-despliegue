from database import db
from models.duenio_model import Duenio
from models.multa_model import Multa 
from sqlalchemy import UniqueConstraint

class Asistencia(db.Model):
    __tablename__ = "Asistencia"
    id = db.Column(db.Integer, primary_key=True)
    dueño_id = db.Column(db.Integer, db.ForeignKey('Duenio.id'), nullable=False)
    id_reunion = db.Column(db.Integer, db.ForeignKey('Reuniones.id'), nullable=False)
    asistio = db.Column(db.Boolean, nullable=False, default=False)
    reunion = db.relationship('Reunion', backref='asistencias')
    dueno = db.relationship('Duenio', backref='asistencias')

    __table_args__ = (UniqueConstraint('dueño_id', 'id_reunion', name='_dueño_reunion_uc'),) 

    def __init__(self, dueño_id, id_reunion, asistio=False):
        self.dueño_id = dueño_id
        self.id_reunion = id_reunion
        self.asistio = asistio

    def save(self):
        if not self.asistio:
            multa = Multa.query.filter_by(dueño_id=self.dueño_id, id_reunion=self.id_reunion).first()
            if multa:
                multa.monto += 100
            else:
                multa = Multa(dueño_id=self.dueño_id, id_reunion=self.id_reunion, monto=100)
            multa.save()
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Asistencia.query.all()

    @staticmethod
    def get_by_id(id):
        return Asistencia.query.get(id)

    def update(self, dueño_id=None, id_reunion=None, asistio=None):
        # Obtener el estado anterior de la asistencia
        asistencia_anterior = Asistencia.query.get(self.id)
        if asistencia_anterior and not asistencia_anterior.asistio and asistio:
            multa = Multa.query.filter_by(dueño_id=self.dueño_id, id_reunion=self.id_reunion).first()
            if multa:
                db.session.delete(multa)
                db.session.commit()
        elif asistencia_anterior and asistencia_anterior.asistio and not asistio:
            multa = Multa.query.filter_by(dueño_id=self.dueño_id, id_reunion=self.id_reunion).first()
            if multa:
                multa.monto += 100
            else:
                multa = Multa(dueño_id=self.dueño_id, id_reunion=self.id_reunion, monto=100)
            multa.save()
        if dueño_id is not None:
            self.dueño_id = dueño_id
        if id_reunion is not None:
            self.id_reunion = id_reunion
        if asistio is not None:
            self.asistio = asistio
        db.session.commit()

    def delete(self):
        if not self.asistio:
            multa = Multa.query.filter_by(dueño_id=self.dueño_id, id_reunion=self.id_reunion).first()
            if multa:
                db.session.delete(multa)
                db.session.commit()
        db.session.delete(self)
        db.session.commit()