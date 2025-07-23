from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, request, redirect, url_for, flash, abort
from flask_limiter import RateLimitExceeded

from config import login_manager, app, db, limiter
from forms import LoginForm, RegisterForm, CommentForm
from datetime import datetime, timezone
from models import User, Comment


def get_current_user_nickname():
    if current_user.is_authenticated:
        return current_user.nickname
    return None


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/comments', methods=['GET', 'POST'])
@limiter.limit("3 per day", key_func=get_current_user_nickname, methods=["POST"])
def comments():
    form = CommentForm()
    all_comments = Comment.query.order_by(Comment.created_at.desc()).all()

    if current_user.is_authenticated:
        if form.validate_on_submit():
            user_id = current_user.id
            # Создаем комментарий
            comment = Comment(
                user_id=user_id,
                text=form.text.data,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий успешно добавлен!', 'success')
            return redirect(url_for('comments'))
        else:
            if request.method == 'POST':
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'error')
    elif not current_user.is_authenticated and form.validate_on_submit():
        flash("Вам нужно сначала войти в аккаунт!", 'danger')

    return render_template('comments.html', comments=all_comments, form=form)


@app.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    flash('Вы достигли лимита комментариев. Попробуйте еще раз позже!', 'warning')
    return render_template('comments.html', comments=Comment.query.order_by(
        Comment.created_at.desc()).all(),form=CommentForm()), 200

@app.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # Проверяем, что текущий пользователь — автор комментария
    if comment.user_id != current_user.id and current_user.nickname != 'admin':
        abort(403)  # Запрещено

    db.session.delete(comment)
    db.session.commit()

    flash('Комментарий удалён.', 'success')
    return redirect(url_for('comments'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        nickname = form.nickname.data
        password = form.password.data

        user = User.query.filter_by(nickname=nickname).first()
        if user and user.check_password(password):
            login_user(user)
            if nickname == 'admin':
                flash('Вы успешно вошли в систему, как администратор!', 'success')
            else:
                flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    else:
        # Если форма не прошла валидацию, ошибки доступны в form.errors
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nickname = form.nickname.data
        password = form.password.data
        repeated_password = form.repeat_password.data

        if User.query.filter_by(nickname=nickname).first() or nickname.lower() == 'admin':
            flash('Это имя пользователя уже занято!', 'danger')
        elif repeated_password != password:
            flash('Пароль не совпадает!', 'danger')
        else:
            user = User(nickname=nickname)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login()
            return redirect(url_for('index'))
    else:
        # Если форма не прошла валидацию, ошибки доступны в form.errors
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'error')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/account_cabinet', methods=['GET', 'POST'])
@login_required
def account_cabinet():
    # users = User.query.all()
    # for user in users:
    #     print(user.id, user.nickname, user.password_hash)

    form = RegisterForm()
    if form.validate_on_submit():
        new_nickname = form.nickname.data
        new_password = form.password.data
        new_repeated_password = form.repeat_password.data

        if new_nickname and new_nickname != current_user.nickname:
            if User.query.filter_by(nickname=new_nickname).first():
                flash('Этот никнейм уже занят', 'danger')
                return redirect(url_for('account_cabinet'))
            elif new_repeated_password != new_password:
                flash('Пароль не совпадает!', 'danger')
                return redirect(url_for('account_cabinet'))
            current_user.nickname = new_nickname

        if new_password:
            current_user.set_password(new_password)

        db.session.commit()
        flash('Данные успешно обновлены', 'success')
        return redirect(url_for('account_cabinet'))
    else:
        # Если форма не прошла валидацию, ошибки доступны в form.errors
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'error')

    return render_template('account_cabinet.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
    
