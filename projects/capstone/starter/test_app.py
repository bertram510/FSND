
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie, db_drop_and_create_all
from datetime import date


class CastAgencyTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.casting_assistant_token = os.environ['casting_assistant_token']
        self.casting_director_token = os.environ['casting_director_token']
        self.executive_producer_token = os.environ['executive_producer_token']
        self.client = self.app.test_client
        self.database_name = "cast_agency_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        db_drop_and_create_all()

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        new_actor = {
            'name': 'Test Name',
            'age': 25,
            'gender': 'Male'
        }

        res = self.client().post('/actors', json=new_actor,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.executive_producer_token)})

        new_movie = {
            'title': 'Test Movie',
            'release_date': '2020-06-17'
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.executive_producer_token)})

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    DONE
    Write at least one test for each test for successful operation
    and for expected errors.
    """
    def test_get_actors(self):
        res = self.client().get('/actors', headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['actors']) > 0)

    def test_401_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['error'], 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_update_actors_by_id(self):
        update_actor = {
            'name': 'John Smith',
            'gender': 'Male'
        }
        res = self.client().patch('/actors/1', json=update_actor,
                                  headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['update_actor']) > 0)

    def test_400_fail_to_update_actors(self):
        update_actor = {
            'name': 'John Smith',
            'gender': 'Male'
        }
        res = self.client().patch('/actors/2', json=update_actor,
                                  headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_update_actors(self):
        update_actor = {
            'name': 'John Smith',
            'gender': 'Male'
        }
        res = self.client().patch('/actors/2', json=update_actor,
                                  headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_delete_actors_by_id(self):
        res = self.client().delete('/actors/1',
                                   headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_actor'], 1)

    def test_400_delete_actors_by_id(self):
        res = self.client().delete('/actors/21234',
                                   headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_delete_actors(self):
        res = self.client().delete('/actors/2',
                                   headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_add_actors(self):
        new_actor = {
            'name': 'John Smith',
            'age': 25,
            'gender': 'Male'
        }

        res = self.client().post('/actors', json=new_actor,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['new_actor'] > 0)
        self.assertTrue(data['actors'] > 0)

    def test_400_fail_to_add_actors(self):
        new_actor = {
            'name': 'John Smith'
        }

        res = self.client().post('/actors', json=new_actor,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_add_actors(self):
        new_actor = {
            'name': 'John Smith',
            'age': 25,
            'gender': 'Male'
        }

        res = self.client().post('/actors', json=new_actor,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_get_movies(self):
        res = self.client().get('/movies', headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['movies']) > 0)

    def test_401_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['error'], 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_update_movies_by_id(self):
        update_movie = {
            'title': 'John Smith',
            'release_date': date.today().isoformat()
        }

        res = self.client().patch('/movies/1', json=update_movie,
                                  headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['update_movie']) > 0)

    def test_400_fail_to_update_movies(self):
        update_movie = {
            'title': 'John Smith',
            'release_date': date.today().isoformat()
        }
        res = self.client().patch('/movies/1999', json=update_movie,
                                  headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_update_movies(self):
        update_movie = {
            'title': 'John Smith',
            'release_date': date.today().isoformat()
        }
        res = self.client().patch('/movies/1', json=update_movie,
                                  headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_delete_movies_by_id(self):
        res = self.client().delete('/movies/1',
                                   headers={
                                    'Authorization': "Bearer {}".format(
                                        self.executive_producer_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_movie'], 1)

    def test_400_delete_movies_by_id(self):
        res = self.client().delete('/movies/21234',
                                   headers={
                                    'Authorization': "Bearer {}".format(
                                        self.executive_producer_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_delete_movies(self):
        res = self.client().delete('/movies/1',
                                   headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_assistant_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_add_movies(self):
        new_movie = {
            'title': 'Inception 2',
            'release_date': date.today().isoformat()
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.executive_producer_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['new_movie'] > 0)
        self.assertTrue(data['movies'] > 0)

    def test_400_fail_to_add_movies(self):
        new_movie = {
            'title': 'Inception 2'
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.executive_producer_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_add_movies(self):
        new_movie = {
            'title': 'Inception 2',
            'release_date': date.today().isoformat()
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers={
                                    'Authorization': "Bearer {}".format(
                                        self.casting_director_token)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
