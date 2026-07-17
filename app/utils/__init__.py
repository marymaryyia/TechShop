import json
import os
from pathlib import Path
from flask import request, session, redirect, url_for, current_app, abort
from functools import wraps
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer
from app.models import MegaGroup, MegaItem, Category, Product


BASE_DIR = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = BASE_DIR / "translations"

_translations_cache = {}
_cache_mtime = {}

def load_translations(lang):
    path = TRANSLATIONS_DIR / f"{lang}.json"
    
    if not path.exists():
        return {}
        
    current_mtime = os.path.getmtime(path)
    
    if lang in _translations_cache and _cache_mtime.get(lang) == current_mtime:
        return _translations_cache[lang]
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            _translations_cache[lang] = data
            _cache_mtime[lang] = current_mtime
            return data
    except Exception:
        return {}

def t(key, default=None):
    lang = session.get("lang", "ka")
    data = load_translations(lang)
    return data.get(key, default or key)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirm',
            max_age=expiration
        )
    except Exception:
        return False
    return email

def safe_next(fallback='main.index'):
    next_url = request.args.get('next') or request.form.get('next') or request.referrer
    if next_url and next_url.startswith('/'):
        return next_url
    return url_for(fallback)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'super_admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def get_mega_menu():
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    result = []
    for cat in categories:
        cat_data = {
            'id': cat.id,
            'slug': cat.slug,
            'icon_class': cat.icon_class,
            'name_ka': cat.name_ka,
            'name_en': cat.name_en,
            'name': cat.name,
            'groups': []
        }
        for group in cat.mega_groups.order_by(MegaGroup.sort_order).all():
            group_data = {
                'title_ka': group.title_ka,
                'title_en': group.title_en,
                'title': group.title,
                'items': []
            }
            for item in group.items.order_by(MegaItem.sort_order).all():
                group_data['items'].append({
                    "name_ka": item.title_ka,
                    "name_en": item.title_en,
                    'name': item.title,
                    'url': item.url
                })
            cat_data['groups'].append(group_data)
        result.append(cat_data)
    return result

def cart_count():
    cart = session.get('cart', {})
    return sum(cart.values())

def wishlist_products():
    ids = session.get('wishlist', [])
    if not ids:
        return []
    return Product.query.filter(Product.id.in_(ids), Product.is_active == True).all()