from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    IntegerField,
    SelectField,
    RadioField,
)
from wtforms.validators import (
    NumberRange,
    ValidationError,
    DataRequired,
    Email,
    EqualTo,
    Length,
)
from app.models import User


class EstatesForm(FlaskForm):
    name = StringField("Názov položky", validators=[DataRequired()])
    description = TextAreaField("Popis položky", validators=[Length(min=1, max=500)])
    # TODO: vyriešiť obrázky
    submit = SubmitField("Pridať položku")


class AddAuctionForm(FlaskForm):
    name = StringField("Názov položky", validators=[DataRequired()])
    start_price = IntegerField(
        "Vyvolávacia cena: ",
        validators=[
            NumberRange(
                min=0,
                max=100000000,
                message="Cena musí byť v povolenom rozsahu 0 až 100 000 000€",
            )
        ],
    )
    open = RadioField(
        "Typ aukcie", choices=[("open", "Otvorená"), ("closed", "Uzavretá")]
    )
    submit = SubmitField("Vytvoriť aukciu")


class EditdAuctionForm(FlaskForm):
    name = StringField("Názov položky", validators=[DataRequired()])
    start_price = IntegerField(
        "Vyvolávacia cena: ",
        validators=[
            NumberRange(
                min=0,
                max=100000000,
                message="Cena musí byť v povolenom rozsahu 0 až 100 000 000€",
            )
        ],
    )
    open = RadioField(
        "Typ aukcie", choices=[("open", "Otvorená"), ("closed", "Uzavretá")]
    )
    submit = SubmitField("Upraviť aukciu")


class EditItemForm(FlaskForm):
    name = StringField("Názov položky", validators=[DataRequired()])
    description = TextAreaField("Popis položky", validators=[Length(min=1, max=500)])
    submit = SubmitField("Uložiť zmeny")


class EditProfileForm(FlaskForm):
    username = StringField("Užívateľské meno", validators=[DataRequired()])
    name = StringField("Krstné meno")
    surname = StringField("Priezvisko")
    submit = SubmitField("Uložiť zmeny")


class LoginForm(FlaskForm):
    username = StringField("Užívateľské meno", validators=[DataRequired()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    remember_me = BooleanField("Zapamätať si")
    submit = SubmitField("Prihlásiť sa")


class RegistrationForm(FlaskForm):
    username = StringField("Užívateľské meno", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    password2 = PasswordField(
        "Zopakovať heslo", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Registrovať")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Užívateľské meno už využité, zvoľte si prosím nové.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email už používaný, zvoľte si prosím iný.")
