from functools import wraps
from flask import render_template, jsonify, session, redirect, request, json, flash
from app import app, models, bcrypt
from app.forms import wallet as wallet_forms
import random
from app.toolbox.multisig_wallet import multisig_wallet

def login_required(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if 'email' in session:
            print(session['email'])
        else:
            return redirect('/user/signin')
        return func(*args, **kwargs)
    return func_wrapper

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/map')
@login_required
def map():
    return render_template('map.html', title='Map')

@app.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    form = wallet_forms.Send()
    username = session['email']    
    user = models.User.query.filter_by(email=username).first()
    address = multisig_wallet.generate_address(str(username))    
    balance = multisig_wallet.get_balance(str(username))

    if(address == None or balance == None):
        return render_template('walleterror.html', title='Error loading wallet service')

    if request.method == 'GET':
        return render_template('wallet.html', title='Wallet', address=address, balance=balance, form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            tx = multisig_wallet.send_bitcoin(username, form.address.data, form.amount.data, user.password)
            # TODO: Use a Bitcoin lib to check if this is a valid hash
            print(tx)
            print(type(tx))
            if (type(tx) is str):
                message = 'You just sent ' + str(form.amount.data) + ' Satoshis to: ' + str(form.address.data) + ' - You may view your transaction at: https://btc.blockr.io/tx/info/' + str(tx)
                flash(message, 'positive')
            elif (tx == False):
                flash('Please enter a valid value', 'negative')
            else:
                flash(tx['message'], 'negative')
            return render_template('wallet.html', title='Wallet', address=address, balance=balance, form=form)
        return render_template('wallet.html', title='Wallet', address=address, balance=balance, form=form)

@app.route('/wallet/generateAddress', methods=['GET'])
@login_required
def wallet_generateAddress():
    username = session['email']    
    address = multisig_wallet.generate_address(str(username))
    if(address == 'Error'):
        return render_template('walleterror.html', title='Wallet Error')
    return jsonify({'address': address})

@app.route('/map/refresh', methods=['POST'])
@login_required
def map_refresh():
    points = [(random.uniform(48.8434100, 48.8634100),
               random.uniform(2.3388000, 2.3588000))
              for _ in range(random.randint(2, 9))]
    return jsonify({'points': points})


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html', title='Test')
