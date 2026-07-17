from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from extensions import db
from app.models import Order, Address  
from app.services.storage import StorageService
from app.utils.products import wishlist_products

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    wishlist_ids = session.get("wishlist", [])
    user_wishlist_products = wishlist_products(product_ids=wishlist_ids)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template(
        "profile.html",
        orders=orders,
        wishlist_products=user_wishlist_products
    )

@profile_bp.route("/profile/avatar", methods=["POST"])
@login_required
def profile_update_avatar():
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename:
            current_user.avatar = StorageService.save(file, folder='uploads')
            db.session.commit()
            flash('Avatar updated.', 'success')
    return redirect(url_for('profile.profile'))

@profile_bp.route("/profile/password", methods=["POST"])
@login_required
def profile_change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
    elif len(new_password) < 6:
        flash('Password must be at least 6 characters.', 'error')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully.', 'success')
    return redirect(url_for('profile.profile'))

@profile_bp.route("/profile/delete", methods=["POST"])
@login_required
def profile_delete():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    session.clear() 
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('main.index'))
@profile_bp.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    
    current_user.phone = phone

    db.session.commit()
    
    flash("პროფილის მონაცემები წარმატებით განახლდა!", "success")
    
    return redirect(url_for('profile.profile') + '#profile')

@profile_bp.route("/profile/address/add", methods=["POST"])
@login_required
def add_address():
    address_type = request.form.get("address_type") 
    if address_type == "Legal":
        full_name = request.form.get("org_name")
        tax_id = request.form.get("tax_id")
    else:
        full_name = f"{request.form.get('first_name')} {request.form.get('last_name')}"
        tax_id = ""

    new_addr = Address(
        user_id=current_user.id,
        label=address_type, 
        full_name=full_name,
        phone=request.form.get("phone"),
        address_line1=request.form.get("address_line1"),
        address_line2=request.form.get("district"), 
        city=request.form.get("city"),
        postal_code=tax_id,
        is_default=(current_user.addresses.count() == 0)
    )
    db.session.add(new_addr)
    db.session.commit()
    flash("მისამართი შენახულია!", "success")
    return redirect(url_for("profile.profile") + "#addresses")

@profile_bp.route("/profile/address/delete/<int:addr_id>", methods=["POST"])
@login_required
def delete_address(addr_id):
    addr = Address.query.filter_by(id=addr_id, user_id=current_user.id).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash("მისამართი წაიშალა.", "success")
    return redirect(url_for("profile.profile") + "#settings")

@profile_bp.route("/profile/order/<int:order_id>")
@login_required
def order_details(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    return render_template("order_details.html", order=order)