import math
import os
import pdfkit
from datetime import datetime as dt
from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from flask_babel import _, lazy_gettext as _l, get_locale, refresh, force_locale
from app import db
from app.printer import bp
from app.models import User, MyCompany, Company


def print_invoice(data):

    def get_texts(language, tax, page, total_pages):
        with force_locale(language):
            # Translate the texts here because the template
            # is not going to be rendered
            texts = {'date': _('Date of issue'),
                     'invoice_to':  _('Invoice to:'),
                     'invoice': _('INVOICE'),
                     'period': _('Billing period'),
                     'period_from': _('From'),
                     'period_to': _('To'),
                     'table_description': _('Description'),
                     'table_unit_cost': _('Unit cost'),
                     'table_quantity': _('Quantity'),
                     'table_amount': _('Amount'),
                     'subtotal':  _('Subtotal'),
                     'taxes': _('Taxes %(tax)%', tax=tax),
                     'discount':  _('Discount'),
                     'total': _('Total'),
                     'payment_method': _('Payment method'),
                     'expiration': _('Pay by'),
                     'notes':  _('Notes'),
                     'acknowledgments': _('Gracias por su confianza.'),
                     'ecomessage': _('Antes de imprimir esta factura, piense '
                                     'bien si es necesario hacerlo. El medio '
                                     'ambiente es cuestión de todos.'),
                     'pages': _('Page %(page)s of %(total)s', page=page+1,
                                total=total_pages)
                     }
        return texts

    # Split the invoice in several pages in case there are many products
    invoice_pages = []
    if len(data['invoice']['products'].keys()) < 9:
        products = data['invoice']['products']
        invoice_pages.append(render_template('/printer/invoice_classic.html',
                             data=data, products=products,
                             texts=get_texts('es_ES', 21, 1, 1),
                             page=1, last=1))
    else:
        if len(data['invoice']['products'].keys()) < 17:
            total_pages = 2
        else:
            total_pages = math.ceil(len(data['invoice']['products'].keys())/16)
        for page in range(math.ceil(len(
                data['invoice']['products'].keys()) / 16)):
            last_in_selection = 17*(page+1) if len(
                data['invoice']['products'].keys()) - 17*page >\
                17 else len(data['invoice']['products'].keys())
            selection = range(17*page + 1, last_in_selection + 1)
            products = {k: data['invoice']['products'][k] for k in
                        data['invoice']['products'].keys() & selection}
            invoice_pages.append(render_template(
                '/printer/invoice_classic.html', data=data, products=products,
                texts=get_texts('es_ES', 21, page, total_pages), page=page+1,
                last=total_pages))

    # Create a temporary folder
    try:
        path = os.path.join(current_app.config['BASEDIR'], 'app', 'temp')
        os.makedirs(path)
    except OSError:
        print("Folder already exists.")

    # Save the rendered pages as html files
    file_id = "{}_{}".format(data['customer']['identifier'],
                             dt.strftime(dt.today(), format="%Y-%b-%d"))
    # Options (not so logical) to print an A4 sheet without top and bottom
    # margins. Wkhtmltopdf applies an internal margin
    options = {'page-size': 'A4', 'encoding': "UTF-8", 'margin-top': '0.01in',
               'margin-bottom': '0.01in', 'margin-left': '1in',
               'margin-right': '0.01in'}
    for i, page in enumerate(invoice_pages):
        with open(current_app.config['BASEDIR'] +
                  '/app/temp/invoice_{}_{}.html'.format(file_id, i + 1),
                  'w', encoding='utf-8') as template:
            template.write(page)
        # Convert the pages html files into pdf files
        pdfkit.from_file(current_app.config['BASEDIR'] +
                         '/app/temp/invoice_{}_{}.html'.format(file_id, i + 1),
                         current_app.config['BASEDIR'] +
                         '/app/temp/invoice_{}_{}.pdf'.format(file_id, i + 1),
                         options=options)

    # Merge the page files into one pdf
    path = os.path.join(current_app.config['BASEDIR'], 'app', 'temp')
    try:
        os.remove(os.path.join(path, 'invoice_{}.pdf'.format(file_id)))
    except OSError:
        print("Error while deleting file")
    os.system("pdftk " + ' "{}"'.format(path + '/invoice_{}*.pdf'.format(
        file_id)) + " cat output " + '"{}"'.format(path +
                                                   '/invoice_{}.pdf'.format(
                                                      file_id)))

    # Remove auxiliary files
    for i, page in enumerate(invoice_pages):
        os.remove(current_app.config['BASEDIR'] +
                  '/app/temp/invoice_{}_{}.html'.format(file_id, i + 1))
        os.remove(current_app.config['BASEDIR'] +
                  '/app/temp/invoice_{}_{}.pdf'.format(file_id, i + 1))
