
from flask import request, url_for

def safe_next(default_endpoint="main.index"):
    nxt = request.values.get("next")
    if nxt and nxt.startswith("/") and not nxt.startswith("//"):
        return nxt
    return url_for(default_endpoint)
