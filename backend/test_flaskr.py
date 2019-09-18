import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432',
            self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {'question': {
            'question': 'new question',
            'answer': 'answer',
            'category': 1,
            'difficulty': 1
        }}

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions_with_results(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['count'], 19)

    def test_get_questions_by_page(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['count'], 19)

    def test_get_questions_with_no_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions_by_category(self):
        res = self.client().post('/questions', json={'category': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['count'], 4)

    def test_get_questions_with_unknown_category(self):
        res = self.client().post('/questions', json={'category': 5000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['count'], 6)

    def test_delete_question_with_valid_id(self):
        res = self.client().delete('/questions/17')

        self.assertEqual(res.status_code, 204)

    def test_delete_question_with_invalid_id(self):
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['created'], 24)
        self.assertEqual(data['count'], 20)

    def test_create_question_already_exists(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 409)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 409)
        self.assertEqual(data['message'], 'Question exists')

    def test_create_question_with_missing_params(self):
        question = {'question': {
            'question': '',
            'category': 1,
            'difficulty': 1
        }}

        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'Check input values')

    def test_get_questions_by_category_id(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])
        self.assertEqual(data['count'], 4)

    def test_quizzes_with_no_category(self):
        res = self.client().post(
            '/quizzes', json={"quiz": {"previous_questions": []}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    def test_quizzes_with_all_category(self):
        res = self.client().post(
            '/quizzes', json={"quiz": {"previous_questions": [],
                                       "category_id": 0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_quizzes_with_no_category(self):
        res = self.client().post(
            '/quizzes', json={"quiz": {"previous_questions": [],
                                       "category_id": 1}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['question']['category'], 1)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
