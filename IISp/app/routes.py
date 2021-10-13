from os import name
from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from app import db

from app.forms import (
    AddAuctionForm,
    EstatesForm,
    LoginForm,
    EditProfileForm,
    RegistrationForm,
    EditItemForm,
    EditdAuctionForm,
)
from app.models import Auction, User, RealEstate
from app import app


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Home")


@app.route("/licitator")
@login_required
def licitator():
    auctions = Auction.query.all()
    return render_template("licitator.html", auctions=auctions)


@app.route("/add_licitator/<int:auction_id>", methods=["POST"])
@login_required
def add_licitator(auction_id):
    auction = Auction.query.get(auction_id)
    auction.licitator_id = current_user.id
    db.session.add(auction)
    db.session.commit()
    return redirect("licitator.html")


@app.route("/make_admin", methods=["POST"])
def make_admin():
    current_user.admin = True
    current_user.licitator = True
    current_user.authorized = True
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for("user", username=current_user.username))


@app.route("/make_licitator", methods=["POST"])
def make_licitator():
    current_user.admin = False
    current_user.licitator = True
    current_user.authorized = True
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for("user", username=current_user.username))


@app.route("/make_host", methods=["POST"])
def make_host():
    current_user.admin = False
    current_user.licitator = False
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for("user", username=current_user.username))


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    items = current_user.get_items()
    auctions = current_user.get_auctions()
    return render_template("user.html", user=user, items=items, auctions=auctions)


@app.route("/auctions")
def auctions():
    auctions = Auction.query.all()
    return render_template("auctions.html", auctions=auctions)


@app.route("/auction_details/<int:auction_id>")
def auction_details(auction_id):
    auction = Auction.query.get(auction_id)
    return render_template("auction_details.html", auction=auction)


@app.route("/edit_auction/<int:auction_id>", methods=["GET", "POST"])
@login_required
def edit_auction(auction_id):
    auction = Auction.query.get(auction_id)
    if auction.creator != current_user:
        abort(403)
    form = EditdAuctionForm()
    if form.validate_on_submit():
        auction.name = form.name.data
        auction.starting_prace = form.start_price.data
        if form.open.data == "open":
            auction.closed = False
        else:
            auction.closed = True
        db.session.commit()
        flash("Zmeny úspešne uložené.")
        return redirect(url_for("auction_details", auction_id=auction.id))
    elif request.method == "GET":
        form.name.data = auction.name
        form.start_price.data = auction.starting_prace
        if auction.closed:
            form.open.data = "closed"
        else:
            form.open.data = "open"
    return render_template(
        "edit_auction.html", auction_id=auction_id, title="Edit auction", form=form
    )


@app.route("/delete_auction/<int:auction_id>")
@login_required
def delete_auction(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    if auction.creator != current_user:
        abort(403)
    db.session.delete(auction)
    db.session.commit()
    messege = "Položka {} úspešne odstránená".format(auction.name)
    flash(messege)
    return redirect(url_for("user", username=current_user.username))


@app.route("/add_auction/<int:item_id>", methods=["GET", "POST"])
@login_required
def add_auction(item_id):
    form = AddAuctionForm()
    item = RealEstate.query.get(item_id)
    if form.validate_on_submit():
        auction = Auction(
            name=form.name.data,
            starting_prace=form.start_price.data,
        )
        if form.open.data == "open":
            auction.closed = False
        else:
            auction.closed = True
        auction.creator_id = current_user.id
        auction.estate_id = item.id
        db.session.add(auction)
        db.session.commit()
        flash("Aukcia úspešne pridaná!")
        return redirect(url_for("user", username=current_user.username))
    return render_template("add_auction.html", title="Add auction", form=form)


@app.route("/add_estate", methods=["GET", "POST"])
@login_required
def add_estate():

    form = EstatesForm()
    if form.validate_on_submit():
        item = RealEstate(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id,
        )
        db.session.add(item)
        db.session.commit()
        flash("Položka úspešne pridaná!")
        return redirect(url_for("user", username=current_user.username))
    return render_template("add_estate.html", title="Add item", form=form)


@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = RealEstate.query.get(item_id)
    if item.owner != current_user:
        abort(403)
    form = EditItemForm()
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("user", username=current_user.username))
    elif request.method == "GET":
        form.name.data = item.name
        form.description.data = item.description
    return render_template(
        "edit_item.html", item_id=item_id, title="Edit item", form=form
    )


@app.route("/delete_item/<int:item_id>")
@login_required
def delete_item(item_id):
    item = RealEstate.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    messege = "Položka {} úspešne odstránená".format(item.name)
    flash(messege)
    return redirect(url_for("user", username=current_user.username))


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.surname.data = current_user.surname
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))
