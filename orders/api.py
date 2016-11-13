import os
from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# initialize the database
db = SQLAlchemy(app)

# custom exception


class ValidationError(ValueError):
    pass


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    # getting the url of a resource
    def get_url(self):
        # url_for  method is used to generate the urls
        return url_for('get_customer', id=self.id, _external=True)

    # generate the json representation
    def export_data(self, data):
        return {
            'self_url': self.get_url,
            'name': self.name
        }

    # creating a new resource and the client is sending a json representation
    # of data
    def import_data(self, data):
        try:
            self.name = data['name']
        # incase name is missing
        except KeyError as e:
            raise ValidationError('Invalid customer: missing ' + e.args[0])
        return self

# get a collection of customers


@app.route('/customers/', method=['GET'])
def get_customers():
    return jsonify({'customers': [customer.get_url() for customer in
                                  Customer.query.all()]})

# getting an individual customer


@app.route('/customers/<int:id>', method=['GET'])
def get_customer(id):
        # if the resource is not there a 404 response will be given
    return jsonify(Customer.query.get_or_404(id).export_data())


@app.route('/customers/', method=['POST'])
def new_customer():
    customer = Customer()
    # request.json will have a dictionary with the decoded json data that the
    # client provided
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({}), 201, {'location': customer.get_url()}

# updating a customer


@app.route('customers/<int:id>', method=['PUT'])
def edit_customer(id):
    # getting a customer from the database
    customer = Customer.query.get_or_404(id)
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({})
