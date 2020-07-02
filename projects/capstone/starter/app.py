import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)

    '''
    @DONE:Set up CORS. Allow '*' for origins.
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @DONE:Use the after_request decorator to set Access-Control-Allow
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
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    # ----------------------------------------------------------------------------#
    # API Endpoints
    # ----------------------------------------------------------------------------#
    '''
    DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()

        if not categories:
            abort(404)

        formatted_categories = [category.format()['type']
                                for category in categories]
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    '''
    DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages. Clicking on the page numbers should
    update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_questions(request, questions)

        if not paginated_questions:
            abort(404)

        categories = Category.query.all()
        formatted_categories = [category.format()['type']
                                for category in categories]

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_category': None
        })

    '''
    DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the
    question will be removed. This removal will persist in the
    database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(400)

        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception:
            abort(422)

    '''
    DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last
    page of the questions list in the "List" tab.
    '''
    @app.route('/addQuestions', methods=["POST"])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if new_question is None:
            abort(400)
        if new_answer is None:
            abort(400)
        if new_category is None:
            abort(400)
        if new_difficulty is None:
            abort(400)

        try:
            question = Question(
                question=new_question, answer=new_answer,
                category=new_category, difficulty=new_difficulty)
            Question.insert(question)

            return jsonify({
                'success': True,
                'questions': len(Question.query.all())
            })
        except Exception:
            abort(422)

    '''
    DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/search', methods=["POST"])
    def search_question():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term is None:
            abort(422)

        questions = Question.query.filter(
            Question.question.ilike('%' + search_term + '%')).all()

        if not questions:
            abort(404)

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(Question.query.all()),
            'current_category': None
        })

    '''
    DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category_id(category_id):
        questions = (Question.query.filter(Question.category == category_id)
                                   .order_by(Question.id)
                                   .all())

        if not questions:
            abort(404)

        paginated_questions = paginate_questions(request, questions)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': category_id
        })

    '''
    DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        quiz_category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions', None)

        if quiz_category is None:
            abort(400)

        if quiz_category['id'] == 0:
            if not previous_questions:
                questions = Question.query.all()
            else:
                questions = (Question.query
                                     .filter(Question.id
                                             .notin_(previous_questions))
                                     .all())
        else:
            if previous_questions is None:
                questions = (Question.query
                                     .filter(Question.category
                                             == quiz_category['id'])
                                     .all())
            else:
                questions = (Question.query
                                     .filter(Question.category
                                             == quiz_category['id'])
                                     .filter(Question.id
                                             .notin_(previous_questions))
                                     .all())

        formatted_questions = [question.format() for question in questions]
        if len(formatted_questions) == 0:
            return jsonify({
                'success': False,
                'question': None
            })

        quiz_question = formatted_questions[
            random.randint(0, len(formatted_questions)) - 1]
        return jsonify({
            'success': True,
            'question': quiz_question
        })

    '''
    DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
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

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)