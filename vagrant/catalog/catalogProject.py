from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Create anti-forgery state token to prevent request forgery.
# Store it in the session for later validation.
@app.route('/login')
def showLogin():
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)
    else:
        return redirect(url_for('showCatalog'))

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # Exchange client token for long-lived server-side token with GET /oauth/accesstoken?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.4/me'
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    
    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<img class="img-rounded" src="'
    output += login_session['picture']
    output += ' " style="width: 96px; height: 96px;"> '
    output += '<h4>Welcome, '
    output += login_session['username']
    output += '!</h4>'
    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/logout')
def logout():
    if 'provider' in login_session:
        provider = login_session['provider']
        if provider == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if provider == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully logged out.')
        return redirect(url_for('showCatalog'))
    else:
        flash('You were not logged in.')
        return redirect(url_for('showCatalog'))

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<img class="img-rounded" src="'
    output += login_session['picture']
    output += ' " style="width: 96px; height: 96px;"> '
    output += '<h4>Welcome, '
    output += login_session['username']
    output += '!</h4>'
    flash("Now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response       

@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.id)).limit(9)
    if 'username' not in login_session:
        return render_template('publicCatalog.html', categories=categories, items=items, login=login_session)
    else:
        return render_template('catalog.html', categories=categories, items=items, login=login_session)

@app.route('/catalog/<string:category_name>')
@app.route('/catalog/<string:category_name>/items')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Item).filter_by(cat_id=category.id)
    if 'username' not in login_session:
        return render_template('publiccategory.html', categories=categories, category=category, items=items, login=login_session, creator=creator)
    else:
        return render_template('category.html', categories=categories, category=category, items=items, login=login_session, creator=creator)

@app.route('/catalog/category/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            newCategory = Category(
                name=request.form['name'], user_id=login_session['user_id'])
            session.add(newCategory)
            flash('Category Successfully Created: %s' % newCategory.name)
            session.commit()
            return redirect(url_for('showCatalog'))
        else:
            return render_template('newCategory.html', login=login_session)

@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        editedCategory = session.query(Category).filter_by(name=category_name).one()
        creator = getUserInfo(editedCategory.user_id)
        if creator.email == login_session['email']:
            if request.method == 'POST':
                if request.form['name']:
                    editedCategory.name = request.form['name']
                    session.add(editedCategory)
                    session.commit()
                    flash('Category Successfully Edited: %s' % editedCategory.name)                    
                    return redirect(url_for('showCatalog'))
            else:
                return render_template('editCategory.html', category=editedCategory, login=login_session)
        else:
            return redirect(url_for('showCategory', category_name=editedCategory.name))
        

@app.route('/catalog/<string:category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        categoryToDelete = session.query(Category).filter_by(name=category_name).one()
        creator = getUserInfo(categoryToDelete.user_id)
        if creator.email == login_session['email']:
            if request.method == 'POST':
                session.delete(categoryToDelete)
                session.commit()
                flash('Category Successfully Deleted: %s' % categoryToDelete.name)                
                return redirect(url_for('showCatalog'))
            else:
                return render_template('deleteCategory.html', category=categoryToDelete, login=login_session)
        else:
            return redirect(url_for('showCategory', category_name=categoryToDelete.name))

@app.route('/catalog/<string:category_name>/<int:item_id>')
def showItem(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name).one()    
    item = session.query(Item).filter_by(id=item_id, cat_id=category.id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session:
        return render_template('publicItem.html', category=category, item=item, login=login_session, creator=creator)
    else:
        return render_template('item.html', category=category, item=item, login=login_session, creator=creator)

@app.route('/catalog/item/new', methods=['GET', 'POST'])
@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name=''):
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            newItem = Item(title=request.form['title'], description=request.form['description'],
                           picture=request.form['picture'], cat_id=request.form['category'],
                           user_id=login_session['user_id'])
            selectedCategory = session.query(Category).filter_by(id=newItem.cat_id).one()
            session.add(newItem)
            session.commit()
            flash('New Item Successfully Created: %s' % (newItem.title))
            return redirect(url_for('showCategory', category_name=selectedCategory.name))
        else:
            if category_name == '':
                category = ''
            else:
                category = session.query(Category).filter_by(name=category_name).one()
            return render_template('newItem.html', categories=categories, currentCategory=category, login=login_session)

@app.route('/catalog/<string:category_name>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()    
    editedItem = session.query(Item).filter_by(id=item_id, cat_id=category.id).one()
    creator = getUserInfo(editedItem.user_id)
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if creator.email == login_session['email']:
            if request.method == 'POST':
                if request.form['title']:
                    editedItem.title = request.form['title']
                if request.form['description']:
                    editedItem.description = request.form['description']
                if request.form['picture']:
                    editedItem.picture = request.form['picture']
                if request.form['category']:
                    editedItem.cat_id = request.form['category']
                session.add(editedItem)
                session.commit()
                selectedCategory = session.query(Category).filter_by(id=editedItem.cat_id).one()
                flash('Item Successfully Edited: %s' % (editedItem.title))
                return redirect(url_for('showCategory', category_name=selectedCategory.name))
            else:
                return render_template('editItem.html', item=editedItem, categories=categories, login=login_session)
        else:
            return redirect(url_for('showItem', category_name=category.name, item_id=editedItem.id))

@app.route('/catalog/<string:category_name>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name).one()    
    itemToDelete = session.query(Item).filter_by(id=item_id, cat_id=category.id).one()
    creator = getUserInfo(itemToDelete.user_id)
    if 'username' not in login_session:
        return redirect(url_for('showItem', category_name=category.name, item_id=itemToDelete.id))
    else:
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash('Item Successfully Deleted: %s' % itemToDelete.title)                
            return redirect(url_for('showCategory', category_name=category.name))
        else:
            return render_template('deleteItem.html', item=itemToDelete, category=category, login=login_session)

@app.route('/catalog.json')
def showJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[c.serialize for c in categories])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
