from flask import session
from app.models import Product

def cart_items():
    cart = session.get('cart', {})
    items = []
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product and product.is_active:
            items.append({
                'product': product,
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.image,
                'qty': qty,
                'line_total': product.price * qty,
                'stock_qty': product.stock_qty
            })
    return items

def cart_count():
    cart = session.get('cart', {})
    return sum(cart.values())