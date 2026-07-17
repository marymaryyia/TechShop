
from flask import Blueprint, jsonify, request
from app.models import Product, Category
from app.utils.cart import cart_count

api_bp = Blueprint('api', __name__)


@api_bp.route('/cart/count')
def api_cart_count():
    return jsonify({'count': cart_count()})


@api_bp.route('/products/search')
def api_product_search():
    """AJAX product search for autocomplete."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        Product.is_active == True,
        Product.name_en.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name_en,
        'slug': p.slug,
        'price': p.price,
        'image': p.image
    } for p in products])