from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(app)


# Product table
class Product(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100))
    price = DB.Column(DB.Integer)
    quantity = DB.Column(DB.Integer, default=0)


# Bill table
class Bill(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    customer = DB.Column(DB.String(100))
    product = DB.Column(DB.String(100))
    price = DB.Column(DB.Integer)
    quantity = DB.Column(DB.Integer)
    total = DB.Column(DB.Integer)


with app.app_context():
    DB.create_all()


# Billing page
@app.route('/', methods=['GET', 'POST'])
def billing():

    total = None
    grand_total = None

    products = Product.query.all()

    if request.method == 'POST':

        customer = request.form['customer']
        product_id = request.form['product']
        quantity = int(request.form['quantity'])

        selected_product = Product.query.get(product_id)

        if selected_product:

            if selected_product.quantity >= quantity:

                price = selected_product.price
                total = price * quantity
                grand_total = total

                # stock कम
                selected_product.quantity -= quantity

                # bill save
                new_bill = Bill(
                    customer=customer,
                    product=selected_product.name,
                    price=price,
                    quantity=quantity,
                    total=grand_total
                )

                DB.session.add(new_bill)
                DB.session.commit()

                return render_template(
                    'billing.html',
                    customer=customer,
                    product=selected_product.name,
                    price=price,
                    quantity=quantity,
                    total=total,
                    grand_total=grand_total,
                    products=products
                )

        return redirect('/')

    return render_template(
        'billing.html',
        products=products
    )


# Products page
@app.route('/products', methods=['GET', 'POST'])
def products():

    if request.method == 'POST':

        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']

        new_product = Product(
            name=name,
            price=price,
            quantity=quantity
        )

        DB.session.add(new_product)
        DB.session.commit()

        return redirect('/products')

    all_products = Product.query.all()

    return render_template(
        'products.html',
        products=all_products
    )


# Bill history
@app.route('/history')
def history():

    bills = Bill.query.order_by(Bill.id.desc()).all()

    return render_template(
        'history.html',
        bills=bills
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)