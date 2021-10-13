from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db
from app import login


class RealEstate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(500))
    image = db.Column(db.LargeBinary)  # alebo mozno len link?
    purchased = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    in_auction = db.relationship("Auction", backref="item", uselist=False)

    def __repr__(self):
        return "<RealEstate {}>".format(self.name)

    def is_listed(self):
        if self.in_auction is None:
            return False
        else:
            return True


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    authorized = db.Column(db.Boolean, default=False)
    licitator = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    estates = db.relationship(
        "RealEstate", backref="owner", lazy="dynamic", foreign_keys="RealEstate.user_id"
    )
    auctions = db.relationship(
        "Auction",
        foreign_keys="Auction.creator_id",
        backref="creator",
        lazy="dynamic",
    )

    licitating = db.relationship(
        "Auction",
        foreign_keys="Auction.licitator_id",
        backref="licitator",
        uselist=False,
    )

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_items(self):
        return self.estates.all()

    def get_auctions(self):
        return self.auctions.all()


class Auction(db.Model):
    id = id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    starting_prace = db.Column(db.Integer)
    in_progress = db.Column(db.Boolean, default=False)
    # open auction - standard, closed - you can bid only once
    closed = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    licitator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    estate_id = db.Column(db.Integer, db.ForeignKey("real_estate.id"))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
