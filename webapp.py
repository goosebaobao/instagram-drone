# -*- coding: utf-8 -*-
from flask import Flask, render_template

from instagram.dao import LIMIT
from instagram.web import instagram
from lib import logging_config

import logging


app = Flask(__name__)
app.config['INS_SEARCH_PAGE_SIZE'] = LIMIT

app.register_blueprint(instagram)


log = logging.getLogger('refusea.webapp')


@app.route('/')
def index():
    return render_template('welcome.jinja2')


if __name__ == '__main__':

    log.debug('webapp start...')
    app.run(port=8080, debug=True)
