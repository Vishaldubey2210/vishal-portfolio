from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    issuer = db.Column(db.String(200))
