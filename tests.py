import unittest
import random
from flask import url_for
from app import create_app, db
from app.printer.routes import print_invoice
from app.models import User, MyCompany, Company, Message, Email
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ModelsCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        print('Checking password verification')
        u = User(username='johndoe')
        u.set_password('unicorn')
        self.assertFalse(u.check_password('pegaso'))
        self.assertTrue(u.check_password('unicorn'))

    def test_avatar(self):
        print('Testing user avatar')
        u = User(username='doctormenta', email='docmenta@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '3e78316a52980015fa844b56052e7b38'
                                         '?d=retro&s=128')),

    def test_user_company(self):
        print('Testing that a user belongs to a company')
        u = User(username='testerguy')
        db.session.add(u)
        mycomp = MyCompany(name='associated testers')
        db.session.add(mycomp)
        mycomp = MyCompany.query.filter_by(name='associated testers').first()
        u.set_company(mycomp.id)
        db.session.add(u)
        db.session.commit()
        self.assertIn(u, mycomp.users)

    def test_user_messages(self):
        print('Testing messages between users')
        sender = User(username='sender')
        db.session.add(sender)
        recipient = User(username='recipient')
        db.session.add(recipient)
        db.session.commit()
        message = Message(body='This a test message', sender_id=sender.id,
                          recipient_id=recipient.id)
        db.session.add(message)
        db.session.commit()
        self.assertEqual(message.sender_id, sender.id)
        self.assertEqual(message.recipient_id, recipient.id)
        self.assertIn(message, sender.messages_sent)
        self.assertIn(message, recipient.messages_received)

    def test_company_relationship(self):
        print('Testing vendor customer relationship')
        vendor = MyCompany(name='Vendor')
        db.session.add(vendor)
        db.session.commit()
        customer = Company(name='Customer', vendor=vendor.id)
        db.session.add(customer)
        db.session.commit()
        self.assertIn(customer, vendor.customers)

    def test_company_emails(self):
        print('Testing mailing to customer')
        vendor = MyCompany(name='Vendor')
        db.session.add(vendor)
        db.session.commit()
        customer = Company(name='Customer', vendor=vendor.id)
        db.session.add(customer)
        db.session.commit()
        email = Email(body='This a test email', sender_id=vendor.id,
                      recipient_id=customer.id)
        db.session.add(email)
        db.session.commit()
        self.assertEqual(email.sender_id, vendor.id)
        self.assertEqual(email.recipient_id, customer.id)
        self.assertIn(email, vendor.emails_sent)

    def test_invoice_printing(self):
        print('Testing the printing of a new invoice')
        data = {'vendor': {'logo_url': "../static/images/logos/logo.svg",
                           'address': "Fake street, 123",
                           'city': 'Springfield',
                           'postal_code': 46900,
                           'province': 'Unknown',
                           'CIF': "76756755646",
                           'phone': '555-56565',
                           'email': 'info@yobusco.com.es'},
                'customer': {'identifier': 'testing',
                             'name': 'Compuhipermegaglobalnet',
                             'address': "Evergreen Terrace, 742",
                             'city': 'Springfield',
                             'postal_code': 46900,
                             'province': 'Unknown',
                             'CIF': "76756755648",
                             'phone': '555-87456',
                             'email': 'info@yobusco.com.es'},
                'invoice': {'identifier': '1254-578',
                            'starting_date': '1 Sep 2019',
                            'ending_date': '1 Oct 2019',
                            'date': '2 Oct 2019',
                            'expiration': '5 Oct 2019',
                            'payment_method': 'Domiciliación bancaria',
                            'notes': 'The prices are randomly generated. The\
                                total cost is not the sum of all the items\
                                    cost. This is just a printing test.',
                            'products': {},
                            'subtotal': 111.00,
                            'tax_percentage': 21,
                            'taxes': 23.31,
                            'discount': 1.00,
                            'total': 134.31,
                            },
                'colors': {'darkest': '#374D80',
                           'dark': '#2C4685',
                           'medium': '#587BCC',
                           'light': '#6E99FF',
                           'lightest': 'rgba(186, 207, 255, 0.7)'}
                }
        for i in range(25):
            data['invoice']['products'][i] = {
                'description': 'Description product {}'.format(i),
                'price_per_unit': random.uniform(0, 1000),
                'amount': random.randrange(20)}
        print_invoice(data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
