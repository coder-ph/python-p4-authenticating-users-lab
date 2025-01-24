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
        # Initialize or increment `page_views`
        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            article = Article.query.filter_by(id=id).first()
            if not article:
                return {'message': 'Article not found'}, 404

            return article.to_dict(), 200

        return {'message': 'Maximum pageview limit reached'}, 401


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        if not username:
            return {'message': 'Username is required'}, 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message': 'Invalid username'}, 404

        session['user_id'] = user.id
        return user.to_dict(), 200


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': '401: Not Authorized'}, 401

        user = User.query.get(user_id)
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        session.clear()
        return {'message': '204: No Content'}, 204


# Register resources with the API
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
