from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import Conflict, NotFound
from http import HTTPStatus
from mysql import connector
import psycopg2

from frameworks_and_drivers.db.mysql import Mysql
from frameworks_and_drivers.db.postgres import PostgreSQL
from interface_adapters.controller.flask_controller import FlaskController
from interface_adapters.presenter.ad_presenter import AdPresenter

app = Flask(__name__)

# MySQL Connection
config = {
    'user': 'root',
    'password': 'password',
    'host': 'mysql',
    'database': 'test_database',
    'autocommit': True
}

# conn = connector.connect(**config)


# PostgreSQL Connection
conn = psycopg2.connect(host='postgres', dbname='test_database', user='root', password='password', port='5432')


@app.route('/memo/<int:memo_id>')
def get(memo_id):
    return jsonify(
        {
            "message": FlaskController(AdPresenter(), PostgreSQL(conn)).get(memo_id)
        }
    )


@app.route('/memo/<int:memo_id>', methods=['POST'])
def post(memo_id):
    return jsonify(
        {
            "message": FlaskController(AdPresenter(), PostgreSQL(conn)).save(memo_id, request)
        }
    )


@app.route('/memo/day', methods=['GET'])
def get_by_day_number():
    return jsonify(
        {
            "message": FlaskController(AdPresenter(), PostgreSQL(conn)).get_by_day_number()
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
