from database import db

class Duenio(db.Model):
    __tablename__ = "Duenio"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    paterno = db.Column(db.String(50), nullable=False)
    materno = db.Column(db.String(50), nullable=False)
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
        db.session.delete(self)
        db.session.commit()