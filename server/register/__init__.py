# -*- coding: utf-8 -*-

from flask import Blueprint


register = Blueprint('register', __name__)


from . import workerspace
from . import dataset