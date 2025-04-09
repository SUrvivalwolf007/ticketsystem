from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user # current_user hier importieren
from . import bp, admin_required
from ..models import db, User, Ticket # Ticket importieren wegen Löschlogik

@bp.route('/users')
@login_required
@admin_required
def user_management():
    users = User.query.order_by(User.last_name, User.first_name).all()
    roles = ['Administrator', 'Techniker', 'Benutzer']
    return render_template('user_management.html', title='Benutzerverwaltung', users=users, roles=roles)

@bp.route('/users/<int:user_id>/set_role', methods=['POST'])
@login_required
@admin_required
def set_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if not new_role or new_role not in ['Administrator', 'Techniker', 'Benutzer']:
        flash('Ungültige Rolle ausgewählt.', 'danger')
        return redirect(url_for('admin.user_management'))

    if user.role == 'Administrator' and user.id == current_user.id:
         admin_count = User.query.filter_by(role='Administrator').count()
         if admin_count <= 1 and new_role != 'Administrator':
             flash('Der letzte Administrator kann nicht herabgestuft werden.', 'warning')
             return redirect(url_for('admin.user_management'))

    user.role = new_role
    try:
        db.session.commit()
        flash(f'Rolle für {user.username} erfolgreich auf {new_role} gesetzt.', 'success')
    except Exception as e:
         db.session.rollback()
         flash(f'Fehler beim Setzen der Rolle: {e}', 'danger')
    return redirect(url_for('admin.user_management'))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)

    if user_to_delete.id == current_user.id:
        flash('Sie können sich nicht selbst löschen.', 'danger')
        return redirect(url_for('admin.user_management'))

    try:
         # Zugewiesene Tickets auf NULL setzen (oder anderem User zuweisen)
         Ticket.query.filter_by(assigned_to_id=user_id).update({'assigned_to_id': None})
         # Erstellte Tickets: Hier muss entschieden werden, was passiert.
         # Vorerst bleiben sie bestehen, zeigen aber auf einen gelöschten User.

         db.session.delete(user_to_delete)
         db.session.commit()
         flash(f'Benutzer {user_to_delete.username} erfolgreich gelöscht.', 'success')
    except Exception as e:
         db.session.rollback()
         flash(f'Fehler beim Löschen des Benutzers: {e}', 'danger')

    return redirect(url_for('admin.user_management'))