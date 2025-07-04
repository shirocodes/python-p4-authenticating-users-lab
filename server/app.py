#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Login(Resource):
    def post(self):
        # Get JSON body from request
        data = request.get_json()
        username = data.get('username')

        if not username:
            return {'error': 'Username is required'}, 400

        # Look up the user in the database
        user = User.query.filter_by(username=username).first()

        if not user:
            return {'error': 'User not found'}, 404

        # Set session key to log the user in
        session['user_id'] = user.id

        return user.to_dict(), 200

class Logout(Resource):
    def delete(self):
        session['user_id'] = None  # Clear session login info
        return {}, 204  # No Content

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {}, 401  # Unauthorized

        user = User.query.get(user_id)
        if not user:
            return {}, 404

        return user.to_dict(), 200

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

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

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
