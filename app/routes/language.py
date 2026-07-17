from flask import Blueprint, redirect, session
from app.utils import safe_next

language_bp = Blueprint('language', __name__)

#language switcher
@language_bp.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in ("ka", "en"):
        session["lang"] = lang_code
        session.modified = True
    return redirect(safe_next())