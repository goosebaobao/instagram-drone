# -*- coding: utf-8 -*-
from flask import Blueprint, render_template,  request

import logging

from instagram.dao import dao

log = logging.getLogger('refusea.instagram.web')

instagram = Blueprint('instagram', __name__, url_prefix='/instagram')
instagram.add_app_template_global()

owners = dao.list_onwers()


@instagram.route('/search')
def search():

    page = 1
    medias = []

    req = request.args
    if req:
        page = int(req.get('page') or page)
        medias = dao.search_medias(
            id=req.get('id'),
            owner=req.get('owner'),
            tag=req.get('tag'),
            page=page)

    return render_template('instagram/search.jinja2', owners=owners, page=page, medias=medias, req=req)
