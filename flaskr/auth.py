import functools
import sys
from eth_account.messages import encode_defunct
from web3.auto import w3
from flask import(Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/login",methods=['POST'])
def login():
    publicAddress = request.form.get('address')

    db = get_db()         
    user = db.execute('SELECT * FROM user WHERE publicAddress = ?', (publicAddress,)).fetchone()

    if user is None:
        db.execute("INSERT INTO user (publicAddress) VALUES (?)", (publicAddress,))
        db.commit()
        user = db.execute('SELECT * FROM user WHERE publicAddress = ?', (publicAddress,)).fetchone()
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
        
@bp.route('/logout',methods=['POST'])
def logout():
    session.clear()
    print("logout", file=sys.stderr)
    return url_for('index')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view