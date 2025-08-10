from database import db
from datetime import datetime

class Multa(db.Model):
    __tablename__ = "Multa"
    
    multa_id = db.Column(db.Integer, primary_key=True)
    duenio_id = db.Column(db.Integer, db.ForeignKey('Duenio.id', ondelete='CASCADE'), nullable=False)
    cuota_id = db.Column(db.Integer, db.ForeignKey('Cuota.cuota_id', ondelete='SET NULL'), nullable=True)
    reunion_id = db.Column(db.Integer, db.ForeignKey('Reunion.id', ondelete='SET NULL'), nullable=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    tipo = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    def __init__(self, duenio_id, monto, tipo, cuota_id=None, reunion_id=None, descripcion=None):
        self.duenio_id = duenio_id
        self.cuota_id = cuota_id
        self.reunion_id = reunion_id
        self.monto = monto
        self.tipo = tipo
        self.descripcion = descripcion

    def save(self):
        if self.tipo not in ['cuota', 'asistencia']:
            raise ValueError("El tipo debe ser 'cuota' o 'asistencia'")
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Multa.query.all()

    @staticmethod
    def get_by_id(multa_id):
        return Multa.query.get(multa_id)
    
    def update(self, duenio_id=None, monto=None, tipo=None, descripcion=None):
        if duenio_id is not None:
            self.duenio_id = duenio_id
        if monto is not None:
            self.monto = monto
        if tipo is not None:
            if tipo not in ['cuota', 'asistencia']:
                raise ValueError("El tipo debe ser 'cuota' o 'asistencia'")
            self.tipo = tipo
        if descripcion is not None:
            self.descripcion = descripcion
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_duenio(duenio_id):
        return Multa.query.filter_by(duenio_id=duenio_id).all()
    
    @staticmethod
    def get_by_tipo(tipo):
        return Multa.query.filter_by(tipo=tipo).all()