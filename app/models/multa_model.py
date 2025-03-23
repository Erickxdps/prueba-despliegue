from database import db

class Multa(db.Model):
    __tablename__ = "Multa"
    id = db.Column(db.Integer, primary_key=True)
    dueño_id = db.Column(db.Integer, db.ForeignKey('Duenio.id'), nullable=False)
    id_reunion = db.Column(db.Integer, db.ForeignKey('Reuniones.id'), nullable=True)
    monto = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, dueño_id, id_reunion=None, monto=0):
        self.dueño_id = dueño_id
        self.id_reunion = id_reunion
        self.monto = monto

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Multa.query.all()

    @staticmethod
    def get_by_id(id):
        return Multa.query.get(id)