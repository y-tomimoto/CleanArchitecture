from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import Conflict, NotFound
from http import HTTPStatus
from memo_handler import MemoHandler
app = Flask(__name__)


@app.route('/memo/<int:memo_id>')
def get(memo_id: int) -> str:
    return jsonify(
        {
            "message": MemoHandler().get(memo_id)
        }
    )


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id: int) -> str:
    memo: str = request.form["memo"]
    return jsonify(
        {
            "message": MemoHandler().save(memo_id, memo)
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
