from database import db
from datetime import datetime

class Cuota(db.Model):
    __tablename__ = "Cuota"
    
    cuota_id = db.Column(db.Integer, primary_key=True)
    terreno_id = db.Column(db.Integer, db.ForeignKey('Terreno.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False, default='Cuota general')  # Título/descripción de la cuota
    descripcion = db.Column(db.Text, nullable=True)  # Descripción detallada (opcional)
    monto = db.Column(db.Float, nullable=False)
    pagado = db.Column(db.Boolean, nullable=False, default=False)
    fecha_creacion = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    terreno = db.relationship('Terreno', backref='cuotas')

    def __init__(self, terreno_id, titulo, monto, descripcion=None, pagado=False):
        self.terreno_id = terreno_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.monto = monto
        self.pagado = pagado

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Cuota.query.all()

    @staticmethod
    def get_by_id(cuota_id):
        return Cuota.query.get(cuota_id)
    
    def update(self, terreno_id=None, titulo=None, descripcion=None, monto=None, pagado=None):
        if terreno_id is not None:
            self.terreno_id = terreno_id
        if titulo is not None:
            self.titulo = titulo
        if descripcion is not None:
            self.descripcion = descripcion
        if monto is not None:
            self.monto = monto
        if pagado is not None:
            self.pagado = pagado
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convierte el objeto Cuota a un diccionario para serialización JSON"""
        return {
            'cuota_id': self.cuota_id,
            'terreno_id': self.terreno_id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'monto': float(self.monto),
            'pagado': self.pagado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    @staticmethod
    def get_by_terreno(terreno_id):
        return Cuota.query.filter_by(terreno_id=terreno_id).all()
    
    @staticmethod
    def get_pendientes():
        return Cuota.query.filter_by(pagado=False).all()