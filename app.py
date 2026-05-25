from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(app)


# -----------------------
# DATABASE MODELS
# -----------------------

class Product(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100))
    price = DB.Column(DB.Integer)
    stock = DB.Column(DB.Integer)


class Bill(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    customer = DB.Column(DB.String(100))
    product = DB.Column(DB.String(100))
    price = DB.Column(DB.Integer)
    quantity = DB.Column(DB.Integer)
    total = DB.Column(DB.Integer)
    date = DB.Column(DB.String(50))


with app.app_context():
    DB.create_all()


# -----------------------
# BILLING PAGE
# -----------------------

@app.route("/", methods=["GET", "POST"])
def billing():

    products = Product.query.all()

    if request.method == "POST":

        customer = request.form["customer"]
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])

        product = Product.query.get(product_id)

        if not product:
            return "Product not found"

        if product.stock < quantity:
            return "Not enough stock"

        total = product.price * quantity

        bill = Bill(
            customer=customer,
            product=product.name,
            price=product.price,
            quantity=quantity,
            total=total,
            date=datetime.now().strftime("%d-%m-%Y %H:%M")
        )

        product.stock -= quantity

        DB.session.add(bill)
        DB.session.commit()

        return render_template(
            "billing.html",
            products=products,
            customer=customer,
            product=product.name,
            price=product.price,
            quantity=quantity,
            total=total,
            grand_total=total
        )

    return render_template("billing.html", products=products)


# -----------------------
# PRODUCTS PAGE
# -----------------------

@app.route("/products", methods=["GET", "POST"])
def products():

    if request.method == "POST":

        name = request.form["name"]
        price = int(request.form["price"])
        stock = int(request.form["stock"])

        new_product = Product(
            name=name,
            price=price,
            stock=stock
        )

        DB.session.add(new_product)
        DB.session.commit()

        return redirect("/products")

    all_products = Product.query.all()

    return render_template(
        "products.html",
        products=all_products
    )


# -----------------------
# DELETE PRODUCT
# -----------------------

@app.route("/delete-product/<int:id>")
def delete_product(id):

    product = Product.query.get(id)

    if product:
        DB.session.delete(product)
        DB.session.commit()

    return redirect("/products")


# -----------------------
# BILL HISTORY
# -----------------------

@app.route("/history")
def history():

    bills = Bill.query.order_by(Bill.id.desc()).all()

    return render_template(
        "history.html",
        bills=bills
    )


# -----------------------
# RUN APP
# -----------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )