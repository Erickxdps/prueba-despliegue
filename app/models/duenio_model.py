from database import db

class Duenio(db.Model):
    __tablename__ = "Duenio"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    paterno = db.Column(db.String(50), nullable=True)
    materno = db.Column(db.String(50), nullable=True)
    ci = db.Column(db.String(20), unique=True, nullable=False)
    multas = db.relationship('Multa', backref='duenio', lazy=True)  # Relación con la tabla Multa

    def __init__(self, nombre, paterno, materno, ci):
        self.nombre = nombre
        self.paterno = paterno
        self.materno = materno
        self.ci = ci

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Duenio.query.all()

    @staticmethod
    def get_by_id(id):
        return Duenio.query.get(id)

    def update(self, nombre=None, paterno=None, materno=None, ci=None):
        if nombre:
            self.nombre = nombre
        if paterno:
            self.paterno = paterno
        if materno:
            self.materno = materno
        if ci:
            self.ci = ci
        db.session.commit()

    def delete(self):
        # Eliminar registros relacionados manualmente para evitar errores de foreign key
        from models.terreno_model import Terreno
        from models.multa_model import Multa
        from models.asistencia_model import Asistencia
        from models.cuota_model import Cuota
        
        try:
            # 1. Obtener todos los terrenos del dueño
            terrenos = Terreno.query.filter_by(duenio_id=self.id).all()
            
            # 2. Eliminar multas y cuotas de todos los terrenos del dueño
            for terreno in terrenos:
                cuotas = Cuota.query.filter_by(terreno_id=terreno.id).all()
                for cuota in cuotas:
                    # Eliminar multas relacionadas a esta cuota
                    multas_cuota = Multa.query.filter_by(cuota_id=cuota.cuota_id).all()
                    for multa in multas_cuota:
                        db.session.delete(multa)
                    
                    # Eliminar la cuota
                    db.session.delete(cuota)
            
            # 3. Eliminar todos los terrenos del dueño
            for terreno in terrenos:
                db.session.delete(terreno)
            
            # 4. Eliminar todas las multas restantes del dueño (tipo 'asistencia' u otras)
            multas_restantes = Multa.query.filter_by(duenio_id=self.id).all()
            for multa in multas_restantes:
                db.session.delete(multa)
            
            # 5. Eliminar todas las asistencias del dueño
            asistencias = Asistencia.query.filter_by(duenio_id=self.id).all()
            for asistencia in asistencias:
                db.session.delete(asistencia)
            
            # 6. Finalmente eliminar el dueño
            db.session.delete(self)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e