import json
import os
from pathlib import Path
from flask import session

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
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        _translations_cache[lang] = data
        _cache_mtime[lang] = current_mtime
        return data

def t(key):
    lang = session.get("lang", "ka")
    data = load_translations(lang)
    return data.get(key, key)