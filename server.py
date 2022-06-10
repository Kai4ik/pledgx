from flask import Flask
from flask_mysqldb import MySQL
from flask_restful import Api
from resources.main import Home
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

# Connecting Flask Application with MySQL
app.config['MYSQL_HOST'] = os.getenv('AZURE_HOSTNAME')
app.config['MYSQL_USER'] = os.getenv('AZURE_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('AZURE_USER_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('AZURE_DATABASE')
app.config['SECRET_KEY'] = "dfkfjfsdhrjsebb"

mysql = MySQL(app)
api = Api(app)

api.add_resource(Home, '/', )


@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


if (__name__ == "__main__"):
    app.run()
