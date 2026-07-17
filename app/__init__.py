import os

from flask import Flask, session
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from extensions import db, migrate, login_manager, csrf, mail

from app.models import User, Category
from app.services.storage import StorageService, LocalStorageProvider
from app.services.translation import t
from app.utils.menu import get_mega_menu
from app.routes.orders import orders_bp
from app.routes.products import products_bp


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production",
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(app.instance_path, "techshop.db"),
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
    # -----------------------------------------

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    app.jinja_env.globals["t"] = t
    StorageService.set_provider(LocalStorageProvider(app.root_path))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.context_processor
    def inject_globals():
        return {
            "t": t,
            "lang": session.get("lang", "ka"),
            "categories": Category.query.order_by(Category.sort_order).all(),
            "mega_menu": get_mega_menu(),
            "cart_count": len(session.get("cart", [])),
            "wishlist_count": len(session.get("wishlist", [])),
            "compare_count": len(session.get("compare", [])),
            "current_user": current_user,
        }

    from .routes.main import main_bp
    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.api import api_bp
    from .routes.cart import cart_bp
    from .routes.wishlist import wishlist_bp
    from .routes.profile import profile_bp
    from .routes.compare import compare_bp
    from .routes.language import language_bp
    from .routes.chatbot import chatbot_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(language_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(chatbot_bp)
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return f"CSRF: {e.description}", 400
        
    return app