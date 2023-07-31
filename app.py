from hack import app, create_db, db
from flask import render_template, redirect, abort, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm, SearchForm, JournalForm
from hack.models import User, Product, UserProduct, Journal
from werkzeug.security import generate_password_hash, check_password_hash
import uuid as uuid
import stripe
from sqlalchemy import or_,desc,asc
from datetime import date
import datetime
stripe.api_key = app.config['STRIPE_SECRET_KEY']

create_db(app)


@app.route('/')
def home():
    searchform = SearchForm()
    # product = Product(category="Supplements",
    #                 name="Keto Gummy Supplements",
    #                 price=199)
    # db.session.add(product)
    # db.session.commit()
    return render_template('index.html', searchform=searchform)

@app.route('/reg', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if form.validate_on_submit():

        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('reg.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ''
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print('hi my name is')
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user)

            next = request.args.get('next')
            if next == None or not next[0] == '/':
                next = url_for('home')
            return redirect(next)
        elif user is not None and user.check_password(form.password.data) == False:
            error = 'Wrong Password'
        elif user is None:
            error = 'No such login Pls create one'
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/explore')
def explore():
    searchform = SearchForm()
    products = Product.query.all()
    return render_template('explore.html', searchform=searchform, products=products)

@app.route('/addtocart/<id>')
@login_required
def addtocart(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        user_product = UserProduct(product_id=product.id, user_id=current_user.id)
        current_user.products.append(user_product)
        db.session.add(current_user)
        db.session.add(product)
        db.session.add(user_product)
        db.session.commit()
        flash('Product added to cart successfully.')
    return redirect(request.referrer)

@app.route('/products/<id>')
def product(id):
    searchform = SearchForm()
    product = Product.query.filter_by(id=id).first()
    prods = Product.query.all()
    prods.remove(product)
    user_products = UserProduct.query.filter_by(user_id=current_user.id).all()
    check=True
    for i in user_products:
        if i.product_id==product.id:
            check=False
    return render_template('product.html', searchform=searchform, prod=product, prods=prods, check=check)

@app.route('/increase_qty/<user_id>/<prod_id>')
@login_required
def increase_qty(user_id, prod_id):
    prod = UserProduct.query.filter_by(user_id=user_id, product_id=prod_id).first()
    if prod.qty != 0:
        prod.qty += 1
    db.session.add(prod)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/sendsearch', methods=['GET', 'POST'])
def send_search():
    form = SearchForm()
    if form.validate_on_submit():
        print(form.query.data)
        return redirect(url_for('return_search', q=form.query.data))
    return redirect(request.referrer)

@app.route('/search')
def return_search():
    searchform = SearchForm()
    query = request.args.get('q')
    results = Product.query.filter(Product.name.like('%' + query + '%')).all()
    return render_template('results.html', searchform=searchform, results=results)

@app.route('/cart')
@login_required
def cart():
    searchform = SearchForm()
    total = 0
    user_products = UserProduct.query.filter_by(user_id=current_user.id).all()

    products = (
        db.session.query(Product)
        .join(UserProduct)
        .filter(UserProduct.user_id == current_user.id)
        .all()
    )

    for entry in current_user.products:
        product = Product.query.filter_by(id=entry.product_id).first()
        total += product.price * entry.qty
    key=app.config['STRIPE_PUBLISHABLE_KEY']
    return render_template('cart.html', searchform=searchform, total=total, key=key, products=products, user_products=user_products)

@app.route('/decrease_qty/<user_id>/<prod_id>')
@login_required
def decrease_qty(user_id, prod_id):
    prod = UserProduct.query.filter_by(user_id=user_id, product_id=prod_id).first()
    if prod.qty == 1:
        current_user.products.remove(prod)
        db.session.delete(prod)
        db.session.commit()
    if prod.qty > 1:
        prod.qty -= 1
        db.session.add(prod)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/thankyou', methods=['GET', 'POST'])
@login_required
def thank_you():
    searchform = SearchForm()
    for i in current_user.products:
        current_user.products.remove(i)
        db.session.delete(i)
        db.session.commit()
    return render_template('thankyou.html', searchform=searchform)

@app.route('/epsilon', methods=['GET', 'POST'])
@login_required
def epsilon():
    if current_user.premium == 1:
        d=date.today()
        d=str(d)
        sum=0
        if current_user.journal==d:
            sum+=1
        if current_user.video==d:
            sum+=1
        if current_user.meditate==d:
            sum+=1
        if current_user.pill==d:
            sum+=1
        percent = sum*100/4
        return render_template('epsilon_new.html',d=d,percent=percent)
    else:
        abort(403)

@app.route('/vidlib', methods=['GET', 'POST'])
@login_required
def vidlib():
    if current_user.premium == 1:
        return render_template('vidlib.html')
    else:
        abort(403)

@app.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    if current_user.premium == 0:
        return render_template('survey.html')
    else:
        abort(403)

@app.route('/timer', methods=['GET', 'POST'])
@login_required
def timer():
    if current_user.premium == 1:
        return render_template('timer.html')
    else:
        abort(403)

@app.route('/getpremium')
@login_required
def get_premium():
    return render_template('getpremium.html')

@app.route('/charge')
@login_required
def charge():
    amount = 599

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='inr',
        description='Premium Subscription Charge'
    )

    current_user.premium = 1
    db.session.commit()

    return render_template('charge.html', amount=amount)



@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    form = JournalForm()
    journal = Journal.query.filter_by(user_id=current_user.id).order_by(Journal.id.desc())
    if form.validate_on_submit():
        data = Journal(text=form.text.data, user_id=current_user.id)
        db.session.add(data)
        db.session.commit()

        return redirect('journal')
    return render_template('journal.html', form=form, journal=journal)

@app.route('/journal/<id>', methods=['GET','POST'])
@login_required
def single(id):
    journal = Journal.query.get(id)
    if journal.user_id != current_user.id:
        abort(403)
    return render_template('journal_single.html' ,journal=journal)

@app.route('/done/<what>/<which>', methods=['GET','POST'])
@login_required
def done(what,which):
    d=date.today()-datetime.timedelta(days=int(which))
    d=str(d)
    if what=='journal':
        current_user.journal=d
    if what=='meditate':
        current_user.meditate=d
    if what=='video':
        current_user.video=d
    if what=='pill':
        current_user.pill=d
    db.session.commit()
    return redirect(url_for("epsilon"))

@app.route('/demopremium', methods=['GET','POST'])
@login_required
def prem():
    current_user.premium=1
    db.session.commit()
    return redirect(url_for("thank_you"))
if __name__ == '__main__':
    app.run(debug=True)
