from flask import Blueprint

bp = Blueprint('main', __name__)


@bp.app_template_filter()
def currency_format(value):
    value = float(value)
    return "{:.2f}".format(value).replace('.', ',')

from app.main import routes