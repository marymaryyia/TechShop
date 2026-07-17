from app.models import Product


def get_product(product_id):
    return Product.query.get_or_404(product_id)

def wishlist_products(product_ids):
    if not product_ids:
        return []
    return Product.query.filter(Product.id.in_(product_ids), Product.is_active == True).all()

def compare_products(product_ids):
    if not product_ids:
        return []
    return Product.query.filter(Product.id.in_(product_ids), Product.is_active == True).all()