# app/tickets/forms.py

from flask_wtf import FlaskForm
# Import für Datei-Upload-Feld:
from flask_wtf.file import FileField, FileAllowed
# Standard WTForms Felder:
from wtforms import StringField, TextAreaField, SubmitField, SelectField
# Validatoren für die Felder:
from wtforms.validators import DataRequired, Length, Email, Optional

# Formular zur Erstellung eines neuen Tickets
class CreateTicketForm(FlaskForm):
    subject = StringField('Betreff',
                          validators=[DataRequired(message="Ein Betreff ist erforderlich."),
                                      Length(max=200)])
    requester_email = StringField('E-Mail des Antragstellers',
                                  validators=[DataRequired(message="E-Mail ist erforderlich."),
                                              Email(message="Bitte geben Sie eine gültige E-Mail-Adresse ein."),
                                              Length(max=120)])
    description = TextAreaField('Beschreibung',
                                validators=[DataRequired(message="Eine Beschreibung ist erforderlich.")])
    attachment = FileField('Anhang (Optional)',
                           validators=[Optional(),
                                       # Optional: Beschränkung der Dateitypen hinzufügen
                                       # FileAllowed(['jpg', 'png', 'pdf', 'zip', 'txt'], 'Nur Bilder, PDF, ZIP oder Textdateien!')
                                      ])
    anydesk_id = StringField('AnyDesk ID (Optional)',
                             validators=[Optional(), Length(max=100)])
    submit = SubmitField('Ticket erstellen')

# Formular zur Bearbeitung wichtiger Ticket-Felder (Status, Zuweisung)
class EditTicketForm(FlaskForm):
    # Status als Dropdown-Auswahlfeld
    status = SelectField('Status', choices=[
        ('Neu', 'Neu'),
        ('In Bearbeitung', 'In Bearbeitung'),
        ('Warten', 'Warten'),
        # ('KI', 'KI'), # Beispiel: Wenn 'KI' Status nicht mehr relevant ist
        ('Geschlossen', 'Geschlossen')
    ], validators=[DataRequired(message="Ein Status ist erforderlich.")])

    # Zuweisung als Dropdown-Auswahlfeld
    # Die 'choices' hierfür werden dynamisch in der Route (view_ticket) gesetzt.
    # coerce=int stellt sicher, dass der ausgewählte Wert (User-ID) als Zahl behandelt wird.
    # Optional() erlaubt die Auswahl von 'Nicht zugewiesen' (was oft den Wert 0 hat).
    assigned_to = SelectField('Zugewiesen an', coerce=int, validators=[Optional()])

    # Optional könnten hier auch Betreff/Beschreibung zur Bearbeitung hinzugefügt werden:
    # subject = StringField('Betreff', validators=[DataRequired(), Length(max=200)])
    # description = TextAreaField('Beschreibung', validators=[DataRequired()])

    submit = SubmitField('Änderungen speichern')