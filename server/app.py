from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, User

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Login(Resource):
    def post(self):
        data = request.json
        if not data or 'username' not in data:
            return {'message': 'Invalid request. Please provide a username in JSON format.'}, 400

        username = data['username']

        try:
            user = User.query.filter_by(username=username).first()

            if user:
                session['user_id'] = user.id
                return {'id': user.id, 'username': user.username}, 200
            else:
                return {'message': 'User not found'}, 404
        except Exception as e:
            return {'message': 'An error occurred while processing the request.', 'error': str(e)}, 500

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            try:
                user = User.query.get(user_id)
                if user:
                    return {'id': user.id, 'username': user.username}, 200
                else:
                    return {'message': 'User not found'}, 404
            except Exception as e:
                return {'message': 'An error occurred while processing the request.', 'error': str(e)}, 500
        else:
            return {}, 401  

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
