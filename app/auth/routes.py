from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from . import bp # Importiere den Blueprint
from .forms import LoginForm, RegistrationForm
from ..models import User, db # Importiere User-Modell und db-Objekt
from urllib.parse import urlsplit

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tickets.ticket_overview')) # Bereits eingeloggt

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username_or_email.data) |
            (User.email == form.username_or_email.data)
        ).first()

        if user is None or not user.check_password(form.password.data):
            flash('Ungültiger Benutzername oder Passwort.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        flash(f'Willkommen zurück, {user.first_name}!', 'success')

        # Weiterleitung zur ursprünglich angeforderten Seite oder zur Übersicht
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('tickets.ticket_overview')
        return redirect(next_page)

    return render_template('login.html', title='Anmelden', form=form)

@bp.route('/logout')
@login_required # Nur eingeloggte User können sich ausloggen
def logout():
    logout_user()
    flash('Sie wurden erfolgreich abgemeldet.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tickets.ticket_overview'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
            # Rolle wird Standard ('Benutzer')
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
        # Optional: Direkt nach Registrierung einloggen:
        # login_user(user)
        # return redirect(url_for('tickets.ticket_overview'))
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Registrieren', form=form)