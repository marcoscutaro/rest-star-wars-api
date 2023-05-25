from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
characterFavorites = db.Table("characterFavorite",
     db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
     db.Column("id", db.Integer, db.ForeignKey("character.id"), primary_key=True)
)

planetsFavorites = db.Table("planetsFavorite",
     db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
     db.Column("id", db.Integer, db.ForeignKey("planet.id"), primary_key=True)
)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    planetsFavorite = db.relationship("Planet", secondary=planetsFavorites,
                                      primaryjoin="User.id==planetsFavorite.c.id",
                                      secondaryjoin="Planet.id==planetsFavorite.c.id",
                                      lazy='subquery',
                                      backref=db.backref("users",  lazy=True))
    characterFavorite = db.relationship("Character", secondary=characterFavorites,
                                      primaryjoin="User.id==characterFavorite.c.id",
                                      secondaryjoin="Character.id==characterFavorite.c.id",
                                      lazy='subquery',
                                      backref=db.backref("users",  lazy=True))

    def __repr__(self):
        return '<User %r>' % self.name

    def serialize_user(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "characterFavorite": self.obtcharacterFavorite(),
            "planetsFavorite": self.obtplanetsFavorite(),         
        }


class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(80), unique=False, nullable=False)

    def serialize_all(self):
        return {
            "id": self.id,
            "name": self.name,
            # do not serialize the password, its a security breach
        }

    def serialize_each(self):
         return {
            "id": self.id,
            "properties":{
                "name": self.name,
                "gender": self.gender
            }
            # do not serialize the password, its a security breach
        }

class Planet(db.Model):
    __tablename__ = "planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.Integer, unique=False, nullable=False)
    diameter = db.Column(db.Integer, unique=False, nullable=False)

    def serialize_all(self):
        return {
            "id": self.id,
            "name": self.name,
            # do not serialize the password, its a security breach
        }

    def serialize_each(self):
         return {
            "id": self.id,
            "properties":{
                "name": self.name,
                "population": self.population,
                "diameter": self.diameter
            }
            # do not serialize the password, its a security breach
        }

    def obtcharacterFavorite(self):
        return list(map(lambda obj: obj.serialize_each(), self.characterFavorites))

    def obtplanetsFavorite(self):
        return list(map(lambda obj: obj.serialize_each(), self.planetsFavorites))



