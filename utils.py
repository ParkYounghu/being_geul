from fastapi import Request

def flash(request: Request, message: str, category: str = "success"):
    if "flash_messages" not in request.session:
        request.session["flash_messages"] = []
    request.session["flash_messages"].append((category, message))

def get_flashed_messages(request: Request):
    return request.session.pop("flash_messages", [])
