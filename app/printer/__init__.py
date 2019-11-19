from flask import Blueprint

bp = Blueprint('printer', __name__)


@bp.app_template_filter()
def currency_format(value):
    value = float(value)
    return "{:.2f}".format(value).replace('.', ',')

from app.printer import routes
