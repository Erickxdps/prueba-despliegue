from database import db

class Terreno(db.Model):
    __tablename__ = "Terreno"
    id = db.Column(db.Integer, primary_key=True)
    duenio_id = db.Column(db.Integer, db.ForeignKey('Duenio.id'), nullable=False)
    lugar = db.Column(db.String(100), nullable=False)
    manzano = db.Column(db.Integer, nullable=False)
    metros_cuadrados = db.Column(db.Integer, nullable=False)
    dueno = db.relationship('Duenio', backref='terrenos')


    def __init__(self, duenio_id, lugar, manzano, metros_cuadrados):
        self.duenio_id = duenio_id
        self.lugar = lugar
        self.manzano = manzano
        self.metros_cuadrados = metros_cuadrados

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Terreno.query.all()

    @staticmethod
    def get_by_id(id):
        return Terreno.query.get(id)

    def update(self, duenio_id=None, lugar=None, manzano=None, metros_cuadrados=None):
        if duenio_id is not None:
            self.duenio_id = duenio_id
        if lugar is not None:
            self.lugar = lugar
        if manzano is not None:
            self.manzano = manzano
        if metros_cuadrados is not None:
            self.metros_cuadrados = metros_cuadrados
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()