from flask import Blueprint, render_template, request, session, abort, redirect, url_for
from sqlalchemy import or_, func
import app.models.models
from extensions import db
from app.utils.products import get_product

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    featured = app.models.models.Product.query.filter_by(is_active=True).order_by(app.models.models.Product.created_at.desc()).limit(8).all()
    hero_slides = app.models.models.HeroSlide.query.filter_by(is_active=True).order_by(app.models.models.HeroSlide.sort_order).all()
    
    brands = app.models.models.Brand.query.order_by(app.models.models.Brand.id).all()
    top_brands = [b.name for b in brands]
    
    return render_template("index.html", featured=featured, hero_slides=hero_slides, brands=brands, top_brands=top_brands)

@main_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    item = get_product(product_id)
    if not item or not item.is_active:
        abort(404)
    related = app.models.models.Product.query.filter(
        app.models.models.Product.category_id == item.category_id, app.models.models.Product.id != item.id, app.models.models.Product.is_active == True
    ).limit(4).all()
    in_wishlist = item.id in session.get("wishlist", [])
    in_compare = item.id in session.get("compare", [])
    reviews = app.models.models.Review.query.filter_by(product_id=item.id, is_approved=True).order_by(app.models.models.Review.created_at.desc()).all()
    return render_template("product.html", product=item, related=related,
                         in_wishlist=in_wishlist, in_compare=in_compare, reviews=reviews)

@main_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        ql = q.lower()
        results = app.models.models.Product.query.filter(
            app.models.models.Product.is_active == True,
            or_(app.models.models.Product.name_ka.ilike(f'%{ql}%'), app.models.models.Product.name_en.ilike(f'%{ql}%'),
                app.models.models.Product.description_ka.ilike(f'%{ql}%'), app.models.models.Product.description_en.ilike(f'%{ql}%'))
        ).all()
    return render_template("search.html", query=q, results=results)


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@main_bp.route("/language/<lang_code>")
def set_language(lang_code):
    if lang_code in ("ka", "en"):
        session["lang"] = lang_code
    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)
    return redirect(url_for("main.index"))