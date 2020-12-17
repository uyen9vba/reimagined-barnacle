from extensions import db

class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    @classmethod
    def get_by_id(cls, tag_id):
        return cls.query.filter_by(id=tag_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls):

        return cls.query.filter_by().all()

