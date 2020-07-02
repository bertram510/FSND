import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Actor, Movie, db_drop_and_create_all
from auth import AuthError, requires_auth

RESULTS_PER_PAGE = 10


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    db_drop_and_create_all()

    '''
    Set up CORS.
    '''
    CORS(app)

    '''
    Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    # ----------------------------------------------------------------------------#
    # Custom Functions
    # ----------------------------------------------------------------------------#
    def paginate_results(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE

        results = [result.format() for result in selection]
        current_results = results[start:end]

        return current_results

    # ----------------------------------------------------------------------------#
    # API Endpoints
    # ----------------------------------------------------------------------------#
    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors():
        actors = Actor.query.all()

        if actors is None:
            abort(404)

        formatted_actors = [actor.format() for actor in actors]

        return jsonify({
            'success': True,
            'actors': formatted_actors
        })

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies():
        movies = Movie.query.all()

        if movies is None:
            abort(404)

        formatted_movies = [movie.format() for movie in movies]

        return jsonify({
            'success': True,
            'movies': formatted_movies
        })

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor_by_id(actor_id):
        actor = Actor.query.filter(
            Actor.id == actor_id).one_or_none()

        if actor is None:
            abort(400)

        try:
            actor.delete()
            return jsonify({
                'success': True,
                'deleted_actor': actor_id
            })
        except Exception:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie_by_id(movie_id):
        movie = Movie.query.filter(
            Movie.id == movie_id).one_or_none()

        if movie is None:
            abort(400)

        try:
            movie.delete()
            return jsonify({
                'success': True,
                'deleted_movie': movie_id
            })
        except Exception:
            abort(422)

    @app.route('/actors', methods=["POST"])
    @requires_auth('create:actors')
    def add_actor():
        body = request.get_json()

        new_name = body.get('name', None)
        new_age = body.get('age', None)
        new_gender = body.get('gender', None)

        if new_name is None:
            abort(400)
        if new_age is None:
            abort(400)
        if new_gender is None:
            abort(400)

        try:
            actor = Actor(
                name=new_name,
                age=new_age,
                gender=new_gender)
            Actor.insert(actor)

            return jsonify({
                'success': True,
                'new_actor': actor.id,
                'actors': len(Actor.query.all())
            })
        except Exception:
            abort(422)

    @app.route('/movies', methods=["POST"])
    @requires_auth('create:movies')
    def add_movie():
        body = request.get_json()

        new_title = body.get('title', None)
        new_release_date = body.get('release_date', None)

        if new_title is None:
            abort(400)
        if new_release_date is None:
            abort(400)

        try:
            movie = Movie(
                title=new_title,
                release_date=new_release_date
                )
            Movie.insert(movie)

            return jsonify({
                'success': True,
                'new_movie': movie.id,
                'movies': len(Movie.query.all())
            })
        except Exception:
            abort(422)

    @app.route('/actors/<int:actor_id>',  methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(payload, actor_id):
        body = request.get_json()

        update_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if update_actor is None:
            abort(400)

        update_name = body.get('name', None)
        update_age = body.get('age', None)
        update_gender = body.get('gender', None)

        try:
            if update_name is not None:
                update_actor.title = update_name
            if update_age is not None:
                update_actor.age = update_age
            if update_gender is not None:
                update_actor.gender = update_gender
            update_actor.update()

            return jsonify({
                'success': True,
                'update_actor': [update_actor.format()]
            })
        except Exception:
            abort(422)

    @app.route('/movies/<int:movie_id>',  methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        body = request.get_json()

        update_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if update_movie is None:
            abort(400)

        update_title = body.get('title', None)
        update_release_date = body.get('release_date', None)

        try:
            if update_title is not None:
                update_movie.title = update_title
            if update_release_date is not None:
                update_movie.release_date = update_release_date
            update_movie.update()

            return jsonify({
                'success': True,
                'update_movie': [update_movie.format()]
            })
        except Exception:
            abort(422)

    # ----------------------------------------------------------------------------#
    # Error Handlers
    # ----------------------------------------------------------------------------#
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def authentification_failed(AuthError):
        return jsonify({
            "success": False,
            "error": AuthError.status_code,
            "message": "authentification failed"
        }), 401

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)