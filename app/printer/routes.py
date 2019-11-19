from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, lazy_gettext as _l, get_locale
from app import db
from app.printer import bp
from app.models import User, MyCompany, Company


def print_invoice():
    data = {'vendor': {'logo_url': "../../static/images/logos/logo.svg",
                       'address': "Azorín, 4B, bajo 1",
                       'city': 'Torrent',
                       'postal_code': 46900,
                       'province', 'Valencia'
                       'CIF': "76756755646",
                       'phone': '653058933',
                       'email': 'info@yobusco.com.es'},
            'customer': {'identifier': '124584',
                         'name': 'Company Name',
                         'address': "Azorín, 4B, bajo 1",
                         'city': 'Torrent',
                         'postal_code': 46900,
                         'province', 'Valencia'
                         'CIF': "76756755646",
                         'phone': '653058933',
                         'email': 'info@yobusco.com.es'},
            'invoice': {'identifier': '1254-578',
                        'starting_date': '1 Sep 2019',
                        'ending_date': '1 Oct 2019',
                        'expiration': '5 Oct 2019',
                        'payment_method': 'Domiciliación bancaria',
                        'notes': '',
                        'products': {1: {'description': 'Descripción larga\
                                                        producto 1',
                                         'price_per_unit': 20.00,
                                         'amount': 1},
                                     2: {'description': 'Producto 2',
                                         'price_per_unit': 20.00,
                                         'amount': 1},
                                     3: {'description': 'Producto 3',
                                         'price_per_unit': 15.50,
                                         'amount': 2},
                                     4: {'description': 'Producto 4',
                                         'price_per_unit': 20.00,
                                         'amount': 1},
                                     5: {'description': 'Producto 5',
                                         'price_per_unit': 20.00,
                                         'amount': 1}
                                     },
                        'subtotal': 111.00,
                        'taxes': 23.31,
                        'discount': 0.00,
                        'total': 134.31,
                        }
            }
    
