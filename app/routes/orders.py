from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Order
from extensions import db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def my_orders():
    # აქ მოგვაქვს შეკვეთები მხოლოდ დალოგინებული მომხმარებლისთვის
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders) # ან ცალკე orders.html
