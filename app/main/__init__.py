from flask import Blueprint

main = Blueprint('main', __name__)

# imported at bottom of file to avoid circular dependencies
from . import views #, errors
