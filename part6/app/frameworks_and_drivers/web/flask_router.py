from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import Conflict, NotFound
from http import HTTPStatus
from interface_adapters.controller.flask_controller import FlaskController
from interface_adapters.presenter.ad_presenter import AdPresenter

app = Flask(__name__)


@app.route('/memo/<int:memo_id>')
def get(memo_id):
    return jsonify(
        {
            "message": FlaskController(AdPresenter()).get(memo_id)
        }
    )


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id):
    return jsonify(
        {
            "message": FlaskController(AdPresenter()).save(memo_id, request)
        }
    )


@app.route('/memo/day', methods=['GET'])
def get_by_day_number():
    return jsonify(
        {
            "message": FlaskController(AdPresenter()).get_by_day_number()
        }
    )


@app.errorhandler(NotFound)
def handle_404(err):
    json = jsonify(
        {
            "message": err.description
        }
    )
    return make_response(json, HTTPStatus.NOT_FOUND)


@app.errorhandler(Conflict)
def handle_409(err):
    json = jsonify(
        {
            "message": err.description
        }
    )
    return make_response(json, HTTPStatus.CONFLICT)
