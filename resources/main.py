from urllib import response
from flask_restful import Resource
from flask import request, jsonify
from datetime import datetime, timezone, timedelta
from resources.schema import createUserSchema
import itertools
import sys
import jwt
sys.path.append('../')


def checkRowExistence(cursor, userDetails):
    cursor.execute(''' SELECT * FROM users where fName=%s AND lName=%s AND jobTitle=%s AND phoneNumber=%s AND country=%s ''',
                   (userDetails["firstName"], userDetails["lastName"], userDetails["jobTitle"], userDetails["phoneNumber"], userDetails["country"]))
    row = cursor.fetchall()
    return len(row) > 0, row


def generateToken(app, firstName, lastName, jobTitle, phoneNumber, country):
    return jwt.encode({"firstName": firstName, "lastName": lastName, "phoneNumber": phoneNumber, "jobTitle": jobTitle,
                       "country": country, "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30)}, app.config["SECRET_KEY"], algorithm="HS256")


def decodeToken(app, request):
    return jwt.decode(request.headers.get(
        'Authorization'), app.config["SECRET_KEY"], algorithms=["HS256"])


class Home(Resource):
    def get(self):
        from server import mysql, app
        # Creating a connection cursor
        cursor = mysql.connection.cursor()

        cursor.execute(''' show tables ''')

        tables = list(itertools.chain(*cursor))
        if 'users' not in tables:
            # Executing SQL Statements
            cursor.execute(''' CREATE TABLE users(uid INT(11) AUTO_INCREMENT PRIMARY KEY, fName VARCHAR(30) NOT NULL, lName VARCHAR(30) NOT NULL, phoneNumber VARCHAR(20) NOT NULL, jobTitle VARCHAR(50) NOT NULL, country VARCHAR(30) NOT NULL) ''')

        # Saving the Actions performed on the DB
        mysql.connection.commit()

        # Closing the cursor
        cursor.close()

        if request.headers.get('Authorization'):
            try:
                userDetails = decodeToken(app, request)

                cursor = mysql.connection.cursor()
                rowExists = checkRowExistence(cursor, userDetails)

                if(rowExists[0]):
                    return jsonify({'user': rowExists[1][0]})
                else:
                    return jsonify({'errorMessage': "Token validation failed"})

            except jwt.ExpiredSignatureError:
                # Signature has expired
                return jsonify({"errorMessage": "Token has expired"})
        else:
            return jsonify({"message": "no previous login"})

    def post(self):
        from server import mysql, app
        errors = createUserSchema.validate(request.form)
        if errors:
            return jsonify({"errorMessage": errors})
        else:
            userDetails = request.form
            firstName = userDetails['firstName']
            lastName = userDetails['lastName']
            phoneNumber = userDetails['phoneNumber']
            jobTitle = userDetails['jobTitle']
            country = userDetails['country']

            cursor = mysql.connection.cursor()
            rowExists = checkRowExistence(cursor, userDetails)

            if (rowExists[0] == False):
                cursor.execute(''' INSERT INTO users(fName, lName, jobTitle, phoneNumber, country) VALUES (%s, %s, %s, %s, %s)''',
                               (firstName, lastName, jobTitle, phoneNumber, country))
                mysql.connection.commit()
                cursor.close()
                encodedToken = generateToken(
                    app, firstName, lastName, jobTitle, phoneNumber, country)

                return jsonify({'token': encodedToken})
            else:
                return jsonify({"errorMessage": "User already exists"})

    def put(self):
        from server import mysql, app
        errors = createUserSchema.validate(request.form)
        if errors:
            return jsonify({"errorMessage": errors})
        else:
            newUserDetails = request.form
            firstName = newUserDetails['firstName']
            lastName = newUserDetails['lastName']
            phoneNumber = newUserDetails['phoneNumber']
            jobTitle = newUserDetails['jobTitle']
            country = newUserDetails['country']

            cursor = mysql.connection.cursor()
            userDetails = decodeToken(app, request)
            rowExists = checkRowExistence(cursor, userDetails)

            if (rowExists[0] == True):
                userDetails = rowExists[1][0]
                cursor.execute(''' UPDATE users set fName=%s, lName=%s,phoneNumber=%s, jobTitle=%s,  country=%s WHERE fName=%s AND lName=%s AND phoneNumber=%s AND jobTitle=%s AND country=%s ''',
                               (firstName, lastName, phoneNumber, jobTitle,  country, userDetails[1], userDetails[2], userDetails[3], userDetails[4], userDetails[5]))
                mysql.connection.commit()
                cursor.close()
                encodedToken = generateToken(
                    app, firstName, lastName, jobTitle, phoneNumber, country)
                return jsonify({'token': encodedToken})
            else:
                return jsonify({"errorMessage": "No such user"})
