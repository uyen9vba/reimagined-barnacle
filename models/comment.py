from extensions import db

class Comment(db.Model):
    __tablename__ = 'comment'

    author = db.Column(db.String(100), db.ForeignKey('user.username'))
    text = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(),
            onupdate=db.func.now())
