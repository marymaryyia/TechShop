from flask import Blueprint, flash, render_template, request, redirect, url_for, session, abort, jsonify
from flask_login import current_user, login_required 
from extensions import db
from app.models import Order, OrderItem, Address, Coupon 
from app.utils.cart import cart_items, cart_count
from app.utils.products import get_product
from app.utils import safe_next

cart_bp = Blueprint('cart', __name__)


@cart_bp.route("/cart")
def cart():
    items = cart_items()
    subtotal = sum(i["line_total"] for i in items)
    return render_template("cart.html", items=items, subtotal=subtotal)

@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id):
    item = get_product(product_id)
    if not item or item.stock_qty <= 0:
        abort(404)
    qty = max(1, request.form.get("qty", 1, type=int))
    cart_data = session.get("cart", {})
    key = str(product_id)
    cart_data[key] = cart_data.get(key, 0) + qty
    session["cart"] = cart_data
    session.modified = True
    return redirect(safe_next())

@cart_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def cart_update(product_id):
    qty = request.form.get("qty", 1, type=int)
    cart_data = session.get("cart", {})
    key = str(product_id)
    if key in cart_data:
        if qty and qty > 0:
            cart_data[key] = qty
        else:
            cart_data.pop(key, None)
    session["cart"] = cart_data
    session.modified = True
    return redirect(safe_next("cart.cart"))

@cart_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def cart_remove(product_id):
    cart_data = session.get("cart", {})
    cart_data.pop(str(product_id), None)
    session["cart"] = cart_data
    session.modified = True
    return redirect(safe_next("cart.cart"))

@cart_bp.route("/checkout")
def checkout():
    items = cart_items()
    if not items:
        return redirect(url_for("main.search"))
        
    subtotal = sum(i["line_total"] for i in items)
    
    applied_code = session.get('applied_promo')
    discount_amount = 0.0
    
    if applied_code:
        coupon = Coupon.query.filter(db.func.lower(Coupon.code) == applied_code.lower()).first()
        if coupon and coupon.is_valid and subtotal >= coupon.min_order:
            if coupon.type == 'percentage':
                discount_amount = (subtotal * coupon.value) / 100
            else: # fixed_amount
                discount_amount = min(coupon.value, subtotal)
            session['discount_amount'] = discount_amount
        else:
            session.pop('applied_promo', None)
            session.pop('discount_amount', None)
            
    discount_amount = session.get('discount_amount', 0.0)
    final_total = max(0.0, subtotal - discount_amount)
    
    return render_template(
        "checkout.html", 
        items=items, 
        subtotal=subtotal, 
        discount_amount=discount_amount,
        final_total=final_total
    )

@cart_bp.route("/apply-promo", methods=["POST"])
def apply_promo():
    data = request.get_json()
    code_input = data.get('code', '').strip()
    
    items = cart_items()
    if not items:
        return jsonify({"success": False, "message": "კალათა ცარიელია"}), 400
        
    subtotal = sum(i["line_total"] for i in items)
    coupon = Coupon.query.filter(db.func.lower(Coupon.code) == code_input.lower()).first()
    
    if not coupon:
        return jsonify({"success": False, "message": "ასეთი პრომოკოდი არ არსებობს"}), 404
        
    if not coupon.is_valid:
        if coupon.is_expired:
            return jsonify({"success": False, "message": "ამ კუპონს ვადა გაუვიდა"}), 400
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return jsonify({"success": False, "message": "ამ კუპონის გამოყენების ლიმიტი ამოიწურა"}), 400
        return jsonify({"success": False, "message": "კუპონი აქტიური არ არის"}), 400
        
    if subtotal < coupon.min_order:
        return jsonify({
            "success": False, 
            "message": f"კუპონის გამოსაყენებლად მინიმალური შეკვეთა უნდა იყოს {coupon.min_order:.2f} ₾"
        }), 400
        
    if coupon.type == 'percentage':
        discount_amount = (subtotal * coupon.value) / 100
    else: 
        discount_amount = min(coupon.value, subtotal)
        
    final_total = max(0.0, subtotal - discount_amount)
    
    session['applied_promo'] = coupon.code
    session['discount_amount'] = discount_amount
    session.modified = True
    
    return jsonify({
        "success": True,
        "message": f"კუპონი წარმატებით გააქტიურდა! (-{coupon.display_value})",
        "new_total": f"{final_total:.2f}",
        "discount_amount": f"{discount_amount:.2f}"
    })

@cart_bp.route("/checkout/confirm", methods=["POST"])
@login_required
def confirm_checkout():
    items = cart_items()
    if not items:
        flash("თქვენი კალათა ცარიელია!", "error")
        return redirect(url_for("cart.cart"))

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    customer_name = f"{first_name} {last_name}" if first_name and last_name else current_user.first_name
    
    email = request.form.get("email")
    phone = request.form.get("phone")
    
    address_id = request.form.get("address_id")
    address_obj = Address.query.get(address_id)
    
    if address_obj:
        shipping_address = f"{address_obj.city}, {address_obj.address_line1}"
    else:
        flash("გთხოვთ აირჩიოთ მისამართი!", "error")
        return redirect(url_for("cart.checkout"))

    subtotal = sum(i["line_total"] for i in items)
    applied_code = session.get('applied_promo')
    discount_amount = 0.0
    coupon_to_update = None

    if applied_code:
        coupon_to_update = Coupon.query.filter(db.func.lower(Coupon.code) == applied_code.lower()).first()
        if coupon_to_update and coupon_to_update.is_valid and subtotal >= coupon_to_update.min_order:
            if coupon_to_update.type == 'percentage':
                discount_amount = (subtotal * coupon_to_update.value) / 100
            else:
                discount_amount = min(coupon_to_update.value, subtotal)
        else:
            flash("გამოყენებული კუპონი აღარ არის აქტიური. გთხოვთ სცადოთ თავიდან.", "error")
            session.pop('applied_promo', None)
            session.pop('discount_amount', None)
            return redirect(url_for('cart.checkout'))

    final_price = max(0.0, subtotal - discount_amount)

    new_order = Order(
        user_id=current_user.id,
        status='pending',
        customer_name=customer_name,
        customer_email=email,
        customer_phone=phone,
        shipping_address=shipping_address
    )
    
    db.session.add(new_order)
    
    if coupon_to_update:
        coupon_to_update.used_count += 1
        db.session.add(coupon_to_update)
        
    db.session.flush()
    
    for item in items:
        item_qty = item.get('quantity') or item.get('qty') or 1
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item['product'].id,
            quantity=item_qty,
            unit_price=item['product'].price
        )
        db.session.add(order_item)
        
    db.session.commit()

    session.pop("cart", None)
    session.pop("applied_promo", None)
    session.pop("discount_amount", None)
    session.modified = True
    
    flash("შეკვეთა წარმატებით გაფორმდა!", "success")
    return redirect(url_for("profile.profile") + "#orders")