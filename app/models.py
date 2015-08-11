from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(75), index=True, unique=True)
	password = db.Column(db.String(75), index=False)

	def __repr__(self):
		return '<User %s>' % (self.email)