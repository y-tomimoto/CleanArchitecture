from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import Conflict, NotFound
from http import HTTPStatus
from application_business_rules.memo_handle_interactor import MemoHandleInteractor

from enterprise_business_rules.entity.memo_object import MemoObject
from interface_adapters.controllers.flask_controller import FlaskController

app = Flask(__name__)


@app.route('/memo/<int:memo_id>')
def get(memo_id: int) -> str:
    return jsonify(
        {
            "message": FlaskController().get(memo_id)
        }
    )


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    return jsonify(
        {
            "message": FlaskController().save(memo_id, request)
        }
    )


@app.route('/memo/day', methods=['GET'])
def get_by_day_number() -> str:
    return jsonify(
        {
            "message": FlaskController().get_by_day_number()
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
