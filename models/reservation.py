from extensions import db


class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    workspace_id = db.Column(db.Integer(), db.ForeignKey("workspace.id"), nullable=False)
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)

    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.start_date).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
