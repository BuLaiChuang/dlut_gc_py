# -*- coding: UTF-8 -*-
import os
import json
# from flask_cors import *
# from flask_cors import CORS

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
from flask import Flask, request

app = Flask(__name__)


@app.route('/index1')
def getcontent():
    return("Hello World!")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5590)