import unittest
from app import create_app, db
from app.models import User, MyCompany, Company
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
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

    def test_company(self):
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
