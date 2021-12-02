import functools
import sys
from eth_account.messages import encode_defunct
from web3.auto import w3
from flask import(Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route('/register', methods = ('GET', 'POST'))
# def register():
#     if request.method =='POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None

#         if username=='': 
#             error = 'Username is required'
#         elif password=='':
#             error = 'Password is required'

#         if error is None:
#             try:
#                 db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)),)
#                 db.commit()
#             except db.IntegrityError:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))
#         flash(error)
#     return render_template('auth/register.html')

# @bp.route('/login',methods = ('GET','POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None
#         user = db.execute(
#             'SELECT * FROM user WHERE username = ?', (username,)
#         ).fetchone()

#         if user is None:
#             error = 'Incorrect username.'
#         elif not check_password_hash(user['password'], password):
#             error = 'Incorrect password.'

#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('index'))

#         flash(error)

#     return render_template('auth/login.html')

@bp.route("/login",methods=['POST'])
def login():
    publicAddress = request.form.get('address')
    signature = request.form.get('signature')

    db = get_db()         
    user = db.execute('SELECT * FROM user WHERE publicAddress = ?', (publicAddress,)).fetchone()

    if user is None:
        db.execute("INSERT INTO user (publicAddress) VALUES (?)", (publicAddress,))
        db.commit()
        user = db.execute('SELECT * FROM user WHERE publicAddress = ?', (publicAddress,)).fetchone()
    message = encode_defunct(text="I'm signing this message!");
    address = w3.eth.account.recover_message(message, signature=signature)
    
    if address == publicAddress:
        session.clear()
        session['user_id'] = user['id']
        print('Hello {}'.format(session['user_id']), file=sys.stderr)
    return url_for('index')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user =None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view