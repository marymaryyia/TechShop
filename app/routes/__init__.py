from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .api import api_bp
from .cart import cart_bp
from .wishlist import wishlist_bp
from .profile import profile_bp
from .compare import compare_bp
from .language import language_bp
from .products import products_bp
from .chatbot import chatbot_bp
__all__ = [
    "main_bp",
    "auth_bp",
    "admin_bp",
    "api_bp",
    "cart_bp",
    "wishlist_bp",
    "profile_bp",
    "compare_bp",
    "language_bp",
    "products_bp",
    "chatbot_bp"
]