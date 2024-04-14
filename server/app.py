from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
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
                return jsonify({'message': 'Logged in successfully', 'user': user.to_dict()}), 200
            else:
                return {'message': 'User not found'}, 404
        except Exception as e:
            return {'message': 'An error occurred while processing the request.'}, 500

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
                return jsonify({'user': user.to_dict()}), 200
            except Exception as e:
                return {'message': 'An error occurred while processing the request.'}, 500
        else:
            return {}, 401

class ClearSession(Resource):
    def delete(self):
        
        session.clear()
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            try:
                article = Article.query.filter(Article.id == id).first()
                if article:
                    return jsonify(article.to_dict()), 200
                else:
                    return {'message': 'Article not found'}, 404
            except Exception as e:
                return {'message': 'An error occurred while processing the request.'}, 500
        else:
            return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
