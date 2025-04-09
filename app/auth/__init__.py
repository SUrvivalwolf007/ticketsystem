from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='../templates/auth') # Template Ordner relativ zum Blueprint

from . import routes # Routen importieren, nachdem bp erstellt wurde