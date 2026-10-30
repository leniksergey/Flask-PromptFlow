from flask import Blueprint

prompts_bp = Blueprint("prompts", __name__, url_prefix="/prompts")

from app.prompts import routes  # noqa: E402, F401
