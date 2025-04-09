from flask import (render_template, redirect, url_for, flash, request,
                   current_app, abort)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_
from . import bp
from .forms import CreateTicketForm
from .forms import EditTicketForm  # Das neue Formular importieren
from .. import db
from ..models import Ticket, User
# app/tickets/routes.py

# Zusätzliche Imports hinzufügen:
from .forms import EditTicketForm  # Das neue Formular importieren
# Optional für Berechtigungen:
# from ..decorators import technician_or_admin_required

# --- ANGEPASSTE view_ticket Funktion ---
@bp.route('/tickets/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
# Optional: @technician_or_admin_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # -> ÄNDERUNG: Variable `edit_form` verwenden statt `form`
    edit_form = EditTicketForm(obj=ticket) # Aktuelle Ticket-Werte ins Formular laden

    # -> WICHTIG: Auswahl für "Zugewiesen an" IMMER laden (vor Validierung und vor Rendering)
    assignable_users = User.query.filter(User.role.in_(['Techniker', 'Administrator'])).order_by(User.username).all()
    edit_form.assigned_to.choices = [(0, 'Nicht zugewiesen')] + \
                                    [(user.id, user.username) for user in assignable_users]

    # Wenn das Formular abgeschickt wurde (POST)
    if edit_form.validate_on_submit(): # -> ÄNDERUNG: `edit_form` verwenden
        # Optional: Berechtigungsprüfung hier, falls kein Decorator verwendet wird

        ticket.status = edit_form.status.data # -> ÄNDERUNG: `edit_form` verwenden
        assigned_id = edit_form.assigned_to.data # -> ÄNDERUNG: `edit_form` verwenden
        ticket.assigned_to_id = assigned_id if assigned_id > 0 else None

        try:
            db.session.commit()
            flash('Ticket erfolgreich aktualisiert.', 'success')
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren des Tickets: {e}', 'danger')

    # Wenn GET Request oder Formular war nicht valide: Template rendern
    # (edit_form.assigned_to.choices wurde oben bereits gesetzt)

    sub_tickets = ticket.children.order_by(Ticket.created_at.asc()).all()

    return render_template('view_ticket.html',
                           title=f'Ticket #{ticket.id}',
                           ticket=ticket,
                           sub_tickets=sub_tickets,
                           edit_form=edit_form) # -> ÄNDERUNG: `edit_form` übergeben
# --- ENDE ANGEPASSTE view_ticket Funktion ---




@bp.route('/tickets')
@login_required
def ticket_overview():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    search_term = request.args.get('search', None)

    query = Ticket.query.order_by(Ticket.created_at.desc())

    if status_filter and status_filter != 'Alle':
         query = query.filter(Ticket.status == status_filter)

    if search_term:
        search_like = f"%{search_term}%"
        query = query.outerjoin(User, Ticket.created_by_id == User.id)\
                     .outerjoin(User, Ticket.assigned_to_id == User.id, aliased=True, name='assignee_user')\
                     .filter(or_(
                         Ticket.subject.ilike(search_like),
                         Ticket.description.ilike(search_like),
                         # Ticket.id Suche (Beispiel, ggf. anpassen)
                         db.cast(Ticket.id, db.String).ilike(search_like),
                         User.username.ilike(search_like),
                         User.first_name.ilike(search_like),
                         User.last_name.ilike(search_like),
                         # TODO: Suche nach zugewiesenem User verbessern, falls nötig
                     ))

    # Hierarchie erstmal ignoriert, zeigt flache Liste
    tickets_pagination = query.paginate(page=page, per_page=15, error_out=False)
    tickets = tickets_pagination.items
    statuses = ['Alle', 'Neu', 'In Bearbeitung', 'Warten', 'KI', 'Geschlossen']

    return render_template('overview.html',
                           title='Ticketübersicht',
                           tickets=tickets,
                           pagination=tickets_pagination,
                           statuses=statuses,
                           current_status=status_filter,
                           current_search=search_term)

@bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = CreateTicketForm()

    max_bytes = current_app.config.get('MAX_CONTENT_LENGTH', 0)
    max_upload_size_mb = max_bytes // 1024 // 1024 if max_bytes else 0

    if request.method == 'GET':
         form.requester_email.data = current_user.email

    if form.validate_on_submit():
        filename = None
        if form.attachment.data:
            f = form.attachment.data
            base_filename = secure_filename(f.filename)
            # !! WICHTIG: Eindeutigen Dateinamen generieren (z.B. mit UUID) für Produktion !!
            filename = base_filename # Nur für Entwicklung OK
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            try:
                f.save(filepath)
            except Exception as e:
                flash(f'Fehler beim Speichern des Anhangs: {e}', 'danger')
                # Wichtig: Formular erneut rendern, nicht redirecten!
                return render_template('create.html',
                                       title='Ticket erstellen',
                                       form=form,
                                       max_upload_size=max_upload_size_mb)

        new_ticket = Ticket(
            subject=form.subject.data,
            requester_email=form.requester_email.data,
            description=form.description.data,
            anydesk_id=form.anydesk_id.data,
            created_by_id=current_user.id,
            attachment_path=filename,
            status='Neu'
        )
        db.session.add(new_ticket)
        try:
            db.session.commit()
            flash('Ticket erfolgreich erstellt!', 'success')
            return redirect(url_for('tickets.ticket_overview'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Speichern des Tickets: {e}', 'danger')

    # GET Request oder invalides Formular: Template rendern
    return render_template('create.html',
                           title='Ticket erstellen',
                           form=form,
                           max_upload_size=max_upload_size_mb)

