from flask import make_response
from flask import request
from flask import abort
from flask import render_template
from flask import jsonify

import json
import os
import sys
import requests
import re
from software import Software

from app import app


def json_dumper(obj):
    """
    if the obj has a to_dict() function we've implemented, uses it to get dict.
    from http://stackoverflow.com/a/28174796
    """
    try:
        return obj.to_dict()
    except AttributeError:
        return obj.__dict__


def json_resp(thing):
    json_str = json.dumps(thing, sort_keys=True, default=json_dumper, indent=4)

    if request.path.endswith(".json") and (os.getenv("FLASK_DEBUG", False) == "True"):
        print u"rendering output through debug_api.html template"
        resp = make_response(render_template(
            'debug_api.html',
            data=json_str))
        resp.mimetype = "text/html"
    else:
        resp = make_response(json_str, 200)
        resp.mimetype = "application/json"
    return resp


def abort_json(status_code, msg):
    body_dict = {
        "HTTP_status_code": status_code,
        "message": msg,
        "error": True
    }
    resp_string = json.dumps(body_dict, sort_keys=True, indent=4)
    resp = make_response(resp_string, status_code)
    resp.mimetype = "application/json"
    abort(resp)


@app.after_request
def after_request_stuff(resp):
    #support CORS
    resp.headers['Access-Control-Allow-Origin'] = "*"
    resp.headers['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, PUT, DELETE, PATCH"
    resp.headers['Access-Control-Allow-Headers'] = "origin, content-type, accept, x-requested-with"

    # without this jason's heroku local buffers forever
    sys.stdout.flush()

    return resp



# FUNCTIONS. move this to another file later.
#
######################################################################################



def print_ip():
    user_agent = request.headers.get('User-Agent')
    # from http://stackoverflow.com/a/12771438/596939
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
    print u"calling from IP {ip}. User-Agent is '{user_agent}'.".format(
        ip=ip,
        user_agent=user_agent
    )


class NotFoundException(Exception):
    pass




# ENDPOINTS
#
######################################################################################


@app.route('/', methods=["GET"])
def index_endpoint():
    return jsonify({
        "version": "0.1",
        "documentation_url": "none yet",
        "msg": "Don't panic"
    })


@app.route("/doi/<path:doi>", methods=["GET"])
def citeas_doi_get(doi):
    my_software = Software()
    my_software.doi = doi
    try:
        my_software.set_citation()
    except NotFoundException:
        abort_json(404, u"No README found at {}".format(url))
    return jsonify(my_software.to_dict())


@app.route("/url/<path:url>", methods=["GET"])
def citeas_url_get(url):
    my_software = Software()
    my_software.url = url
    try:
        my_software.set_citation()
    except NotFoundException:
        abort_json(404, u"No README found at {}".format(url))
    return jsonify(my_software.to_dict())





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

















