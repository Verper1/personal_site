from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    nickname = StringField("Никнейм: ", validators=[DataRequired()])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Подтвердить")


class RegisterForm(FlaskForm):
    nickname = StringField("Никнейм: ", validators=[DataRequired()])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=6)])
    repeat_password = PasswordField("Повторить пароль: ", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Подтвердить")


class CommentForm(FlaskForm):
    text = TextAreaField(
        'Комментарий',
        validators=[
            DataRequired(message='Введите текст комментария'),
            Length(max=300, message='Максимальная длина комментария — 300 символов')
        ],
        render_kw={"rows": 3, "cols": 60}
    )
    submit = SubmitField('Отправить')
