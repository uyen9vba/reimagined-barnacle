from extensions import db
from models.tag import Tag


class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    uuid = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    private = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    cover_image = db.Column(db.String(100), default=None)
    author = db.Column(db.String(100), db.ForeignKey('user.username'))
    tags = db.Column(db.ARRAY(db.String(100)))

    @classmethod
    def get_all(cls, private=None):
        if private is None:
            return cls.query.filter_by(private=False).all()
        else:
            return cls.query.filter_by(private=True).all()

    @classmethod
    def get_by_id(cls, image_id):
        return cls.query.filter_by(id=image_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_by_user(cls, author, visibility=None):
        if visibility == 'public':
            return cls.query.filter_by(author=author, private=False).all()
        elif visibility == 'private':
            return cls.query.filter_by(author=author, private=True).all()
        else:
            return cls.query.filter_by(author=author).all()

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.query.filter_by(uuid=uuid).first()
