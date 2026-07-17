from flask import Blueprint, request, session
from app.utils.cart import cart_count
from app.utils import get_mega_menu, t

main_bp = Blueprint('main', __name__)

@main_bp.app_context_processor
def inject_globals():
    categories = get_mega_menu()
    return {
        "t": t,
        "lang": session.get("lang", "ka"),
        "cart_count": cart_count(),
        "wishlist_count": len(session.get("wishlist", [])),
        "compare_count": len(session.get("compare", [])),
        "categories": categories,
        "mega_menu": categories, 
        "menu": categories,
        "category_lookup": {c.slug: c for c in categories}, 
        "request": request,
    }
