from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_babel import lazy_gettext as _l
from app.models import Product


class AddProduct(FlaskForm):
    ID = StringField(_l('Identifier *'), validators=[DataRequired()])
    name = StringField(_l('Name *'), validators=[DataRequired()])
    price = DecimalField(_l('Cost per unit'), places=2, default=0.00)
    submit_add = SubmitField(_l('Save product'))

    def validate_ID(self, ID):
        product = Product.query.filter_by(
            ID=self.ID.data).first()
        if product is not None:
            raise ValidationError(_l('A product with this identifier\
                 already exists.'))


class EditProduct(FlaskForm):
    ID = StringField(_l('Identifier *'), validators=[DataRequired()])
    name = StringField(_l('Name *'), validators=[DataRequired()])
    price = DecimalField(_l('Cost per unit'), places=2, default=0.00)
    submit_add = SubmitField(_l('Save product'))

    def __init__(self, data, *args, **kwargs):
        super(EditProduct, self).__init__(*args, **kwargs)
        self.original_ID = data['ID']
        self.original_name = data['name']
        self.original_price = data['price']

    def validate_ID(self, ID):
        if ID.data != self.original_ID:
            product = Product.query.filter_by(
                ID=self.ID.data).first()
            if product is not None:
                raise ValidationError(_l('A product with this identifier\
                     already exists.'))
