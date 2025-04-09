from flask import Blueprint

bp = Blueprint('tickets', __name__, template_folder='../templates/tickets')

from . import routes