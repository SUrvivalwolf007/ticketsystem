from flask import Blueprint

bp = Blueprint('admin', __name__, template_folder='../templates/admin')

from ..decorators import admin_required # Wird in routes verwendet

from . import routes