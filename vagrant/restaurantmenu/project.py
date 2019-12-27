from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Restaurant, MenuItem

# Create flask application
app = Flask(__name__)

# Setup database session
engine=create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
Base.metadata.bind=engine
session_factory=sessionmaker(bind=engine)
DBSession = scoped_session(session_factory)
session = DBSession()

# API JSON endpoint
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
    items=session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
    items=session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    
    return render_template('menu.html', restaurant=restaurant, items=items)

# Task 1: Create route for newMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:   
        return render_template('newMenuItem.html', restaurant_id=restaurant_id)

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['newname']:
            editedItem.name = request.form['newname']
        session.add(editedItem)
        session.commit()
        flash("Menu item edited")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(editedItem)
        session.commit()
        flash("Menu item deleted")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=editedItem)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug=True
    app.run(host='0.0.0.0', port=5000)