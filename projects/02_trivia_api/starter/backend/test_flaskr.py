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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']) == 6)
    
    def test_405_get_categories(self):
        res = self.client().delete('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_questions(self):
        res = self.client().get('/questions', json={'category:' : 'science'})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'] > 0)
    
    def test_405_get_questions(self):
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_questions_by_category_id(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], 2)

    def test_404_get_questions_by_category_id(self):
        """Test 400 if no questions with queried category is available."""
        res = self.client().get('/categories/13145/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_and_delete_question(self):
        new_question_valid = {
            'question' : 'Test Question',
            'answer' : 'Test Answer',
            'category' : '2',
            'difficulty' : 3
        } 
        # Test adding question
        res = self.client().post('/addQuestions', json = new_question_valid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'] > 0)
        
        # Test deleting question
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 2)

    def test_400_fail_to_add_question(self):
        new_question_invalid = {
            'question' : 'Test Question',
            'category' : '2',
            'difficulty' : 3
        } 

        res = self.client().post('/addQuestions', json = new_question_invalid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_400_delete_question(self):
        res = self.client().delete('/questions/{}'.format(1314))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_search_question(self):
        search_term_valid = {
            'searchTerm' : 'title',
        } 

        res = self.client().post('/search', json = search_term_valid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_404_search_question(self):
        search_term_invalid = {
            'searchTerm' : 'xxxxxxxxxxx',
        } 

        res = self.client().post('/search', json = search_term_invalid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions(self):
        res = self.client().get('/questions', json={'category:' : 'science'})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'] > 0)
    
    def test_405_get_questions(self):
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'method not allowed')

    def test_quiz(self):
        test_quiz_data_valid = {
            'previous_questions' : [2],
            'quiz_category' : {
                'type' : 'Art',
                'id' : '2'
                }
        } 
        res = self.client().post('/quizzes', json = test_quiz_data_valid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        self.assertTrue(data['question']['id'] not in test_quiz_data_valid['previous_questions'])
    
    def test_400_quiz_no_category(self):
        test_quiz_data_invalid = {
            'previous_questions' : [2]
        } 
        res = self.client().post('/quizzes', json = test_quiz_data_invalid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertFalse(data['success'])        
        self.assertEqual(data['message'], 'bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()