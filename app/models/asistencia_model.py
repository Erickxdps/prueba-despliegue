from database import db
from sqlalchemy import UniqueConstraint

class Asistencia(db.Model):
    __tablename__ = "Asistencia"
    id = db.Column(db.Integer, primary_key=True)
    duenio_id = db.Column(db.Integer, db.ForeignKey('Duenio.id', ondelete='CASCADE'), nullable=False)
    id_reunion = db.Column(db.Integer, db.ForeignKey('Reunion.id', ondelete='CASCADE'), nullable=False)
    asistio = db.Column(db.Boolean, nullable=False, default=False)
    
    reunion = db.relationship('Reunion', backref='asistencias')
    dueno = db.relationship('Duenio', backref='asistencias')

    __table_args__ = (UniqueConstraint('duenio_id', 'id_reunion', name='_duenio_reunion_uc'),) 

    def __init__(self, duenio_id, id_reunion, asistio=False):
        self.duenio_id = duenio_id
        self.id_reunion = id_reunion
        self.asistio = asistio

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Asistencia.query.all()

    @staticmethod
    def get_by_id(id):
        return Asistencia.query.get(id)

    def update(self, duenio_id=None, id_reunion=None, asistio=None):  # ✅ Quitar monto_multa
        if duenio_id is not None:
            self.duenio_id = duenio_id
        if id_reunion is not None:
            self.id_reunion = id_reunion
        if asistio is not None:
            self.asistio = asistio
        db.session.commit()