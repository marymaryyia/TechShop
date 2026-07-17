from flask import (
    Blueprint, render_template, redirect, session, abort, request, flash, url_for
)
from app.utils.products import get_product, wishlist_products
from app.utils import safe_next
from flask_wtf.csrf import CSRFProtect 

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route("/wishlist")
def wishlist():
    wishlist_ids = session.get("wishlist", []) 
    return render_template("wishlist.html", products=wishlist_products(wishlist_ids))
    
@wishlist_bp.route("/wishlist/toggle/<int:product_id>", methods=["POST"])
def wishlist_toggle(product_id):
    if not get_product(product_id):
        abort(404)
        
    ids = session.get("wishlist", [])
    
    if product_id in ids:
        ids.remove(product_id)
        flash("პროდუქტი ამოღებულია სურვილების სიიდან", "info")
    else:
        ids.append(product_id)
        flash("პროდუქტი დამატებულია სურვილების სიაში", "success")
        
    session["wishlist"] = ids
    session.modified = True
    
    return redirect(url_for('wishlist.wishlist'))
