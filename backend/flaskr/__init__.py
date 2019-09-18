import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randint

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATH, DELETE, OPTIONS')

        return response

    @app.route('/questions', methods=['GET'])
    def get_questions():
        """Returns questions and available categories."""

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        selection = Question.query.all()
        categories_selection = Category.query.all()
        if not selection:
            abort(404)

        questions = [question.format() for question in selection[start:end]]
        categories = [category.format() for category in categories_selection]
        if not questions:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(selection),
            'categories': categories,
            'current_category': None
        })

    @app.route('/categories', methods=['GET'])
    def get_categories():
        """Returns available categories."""

        selection = Category.query.all()
        if not selection:
            abort(404)
        categories = [category.format() for category in selection]
        return jsonify({
            'success': True,
            'count': len(categories),
            'categories': categories
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category_id(category_id):
        """Returns questions by given category ID.

        Parameters:
        category_id -- the integer is of the category
        """

        category = Category.query.get(category_id)
        selection = Question.query.filter_by(category=category.id)
        if not selection:
            abort(404)
        questions = [questions.format() for questions in selection]
        return jsonify({
            'success': True,
            'count': len(questions),
            'questions': questions,
            'current_category': category.type
        })

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        """Deletes a question by ID.

        Parameters:
        id -- the ID of the question
        """

        question = Question.query.get(id)
        if not question:
            abort(404)
        question.delete()

        selection = Question.query.all()
        if not selection:
            abort(404)

        questions = [question.format() for question in selection]
        if not questions:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        }), 200

    @app.route('/questions', methods=['POST'])
    def post_questions():
        """Creates a question or searches by term or category.

        A POST to this endpoint will create a new Question if
        the body is a JSON object with the name 'question' If the
        JSON body contains category search will be performed
        for questions with that category. If a search term is
        provided questions will be returned that contain that term.


        JSON Accepted Values:
        category -- category ID
        search -- search term
        question -- a new question to be created
        """

        body = request.get_json()

        category_query = body.get('category')
        search_query = body.get('search')
        new_question = body.get('question')

        status_code = 200
        if category_query:
            selection = Question.query.filter_by(category=category_query)
            if not selection:
                abort(404)
        elif search_query:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search_query)))
            if not selection:
                abort(404)
        elif new_question:
            try:
                question_text = new_question['question']
                answer_text = new_question['answer']
                difficulty = new_question['difficulty']
                category = new_question['category']
            except:
                abort(422)

            existing_question = Question.query.filter_by(
                question=question_text).all()
            if existing_question:
                abort(409)

            try:
                question = Question(question=question_text, answer=answer_text,
                                    difficulty=difficulty, category=category)
                question.insert()
                selection = Question.query.all()
                status_code = 201
            except:
                abort(422)
        else:
            abort(422)

        if not selection:
            abort(404)

        questions = [question.format() for question in selection]
        if not questions:
            abort(404)
        if status_code == 201:
            return jsonify({
                'success': True,
                'questions': questions,
                'created': question.id,
                'count': len(questions)
            }), status_code
        else:
            return jsonify({
                'success': True,
                'questions': questions,
                'count': len(questions)
            }), status_code

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        """Returns a quiz question.

        A quiz question is returned by randomly selecting a
        question from a list of questions that have not
        been shown before for this game. If not category ID
        is provided a random question from all questions returned
        else a question is returned from the category requested.

        JSON Accepted values:
        quiz -- An object that holds a category ID and previous questions
        category_id -- The ID for a category requested
        previous_questions -- A list of previous questions ID's or empty list
        """

        body = request.get_json()

        quiz_data = body.get('quiz')
        if not quiz_data:
            abort(422)
        try:
            category_id = quiz_data['category_id']
        except:
            abort(422)

        if not category_id or category_id == "0":
            selection = Question.query.all()
            category = ""
        else:
            category_query = Category.query.get(category_id)
            category = category_query.format()
            selection = Question.query.filter(
                Question.category == category_id)

        previous_questions = quiz_data['previous_questions']

        questions = [question.format() for question in selection[:5]
                     if question.id not in previous_questions]
        if questions:
            question = questions[randint(0, len(questions)-1)]
        else:
            question = None
        return jsonify({
            'success': True,
            'question': question,
            'previous_questions': previous_questions,
            'current_category': category
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(409)
    def resource_already_exists(error):
        return jsonify({
            'success': False,
            'error': 409,
            'message': 'Question exists'
        }), 409

    @app.errorhandler(422)
    def not_processable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Check input values'
        }), 422

    @app.errorhandler(500)
    def fatal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Oops! Internal server error.'
        }), 500

    return app
