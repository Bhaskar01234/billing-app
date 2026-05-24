from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(app)

class Product(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100))
    price = DB.Column(DB.Integer)

with app.app_context():
    DB.create_all()

@app.route('/', methods=['GET', 'POST'])
def billing():

    total = None
    grand_total = None

    if request.method == 'POST':

        customer = request.form['customer']
        product = request.form['product']
        price = int(request.form['price'])
        quantity = int(request.form['quantity'])

        total = price * quantity
        grand_total = total

        return render_template(
            'billing.html',
            customer=customer,
            product=product,
            price=price,
            quantity=quantity,
            total=total,
            grand_total=grand_total
        )

    return render_template('billing.html')

@app.route('/products', methods=['GET', 'POST'])
def products():

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']

        new_product = Product(name=name, price=price)

        DB.session.add(new_product)
        DB.session.commit()

        return redirect('/products')

    all_products = Product.query.all()

    return render_template('products.html', products=all_products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)