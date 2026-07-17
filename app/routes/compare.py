import json
from flask import (
    Blueprint, render_template, redirect, session, abort, flash, url_for, request
)
from app.utils.products import compare_products, get_product
from app.utils import safe_next

compare_bp = Blueprint('compare', __name__)

@compare_bp.route("/compare")
def compare():
    compare_ids = session.get("compare", [])
    products = compare_products(compare_ids)
    
    all_specs = []  
    spec_map = {}   
    
    for p in products:
        spec_map[p.id] = {}
        
       
        raw_specs = getattr(p, 'specs', {})
        
        if isinstance(raw_specs, str):
            try:
                specs_dict = json.loads(raw_specs)
            except Exception:
                specs_dict = {}
        elif isinstance(raw_specs, dict):
            specs_dict = raw_specs
        else:
            specs_dict = {}
        for key, val in specs_dict.items():
            if key.lower() == 'type':
                continue
                
            if key not in all_specs:
                all_specs.append(key)
            spec_map[p.id][key] = val

    return render_template(
        "compare.html", 
        products=products, 
        all_specs=all_specs, 
        spec_map=spec_map
    )

@compare_bp.route("/compare/toggle/<int:product_id>", methods=["POST"])
def compare_toggle(product_id):
    product = get_product(product_id)
    if not product:
        abort(404)
        
    ids = session.get("compare", [])
    
    if product_id in ids:
        ids.remove(product_id)
        session["compare"] = ids
        session.modified = True
        return redirect(safe_next())
        
    if ids:
        existing_products = compare_products(ids)
        if existing_products:
            first_prod = existing_products[0]
            first_cat = getattr(first_prod.category, 'id', getattr(first_prod, 'category_id', None))
            current_cat = getattr(product.category, 'id', getattr(product, 'category_id', None))
            
            if first_cat != current_cat:
                flash("compare_category_mismatch", "danger")
                return redirect(url_for('compare.compare'))
                
    if len(ids) < 4:
        ids.append(product_id)
        
    session["compare"] = ids
    session.modified = True
    return redirect(safe_next())

@compare_bp.route("/compare/clear", methods=["POST"])
def compare_clear():
    session.pop("compare", None)
    session.modified = True
    return redirect(url_for("compare.compare"))