from flask import Blueprint

present = Blueprint("present", __name__)

from . import views