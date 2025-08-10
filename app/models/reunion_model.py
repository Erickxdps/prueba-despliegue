from database import db
from datetime import date, time

class Reunion(db.Model):
    __tablename__ = "Reunion"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    monto_multa = db.Column(db.Float, nullable=False, default=100.0)  # ✅ NUEVO ATRIBUTO

    def __init__(self, fecha, hora, descripcion=None, monto_multa=100.0):
        self.fecha = fecha
        self.hora = hora
        self.descripcion = descripcion
        self.monto_multa = monto_multa

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Reunion.query.all()

    @staticmethod
    def get_by_id(id):
        return Reunion.query.get(id)

    def update(self, fecha=None, hora=None, descripcion=None, monto_multa=None):
        if fecha is not None:
            self.fecha = fecha
        if hora is not None:
            self.hora = hora
        if descripcion is not None:
            self.descripcion = descripcion
        if monto_multa is not None:
            self.monto_multa = monto_multa
        db.session.commit()

    def delete(self):
        # Eliminar registros relacionados manualmente para evitar errores de foreign key
        from models.asistencia_model import Asistencia
        from models.multa_model import Multa
        
        try:
            # 1. Eliminar todas las asistencias de esta reunión
            asistencias = Asistencia.query.filter_by(id_reunion=self.id).all()
            for asistencia in asistencias:
                db.session.delete(asistencia)
            
            # 2. Desvincular multas relacionadas con esta reunión (SET NULL)
            multas = Multa.query.filter_by(reunion_id=self.id).all()
            for multa in multas:
                multa.reunion_id = None
            
            # 3. Finalmente eliminar la reunión
            db.session.delete(self)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e