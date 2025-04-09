from app import create_app, db
from app.models import User, Ticket
import os
from flask import current_app

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Ticket': Ticket}

if __name__ == '__main__':
    # Sicherstellen, dass der Upload-Ordner existiert beim Start
    # (wird auch in create_app gemacht, aber doppelt hält besser)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'])
        except OSError as e:
             app.logger.error(f"Konnte Upload-Ordner nicht erstellen: {e}") # Besser loggen
    # Debug=True nur für Entwicklung! In Produktion False setzen.
    app.run(debug=True)