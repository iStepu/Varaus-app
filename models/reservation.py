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

    @classmethod
    def get_by_workspace_and_timeslot(cls, workspace_id, start_date, end_date):
        return cls.query.filter(
            workspace_id == cls.workspace_id,
            db.or_(
                db.and_(start_date <= cls.start_date, cls.start_date < end_date),
                db.and_(start_date < cls.end_date, cls.end_date <= end_date))).all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
