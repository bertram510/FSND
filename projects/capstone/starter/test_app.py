
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie, db_drop_and_create_all
from datetime import date

bearer_tokens = {
    "casting_assistant": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImN5S0NzTE5yS01UblpfTUhjdERTaSJ9.eyJpc3MiOiJodHRwczovL2JlcnJ0YW01MTAudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlZmEyYTBkZmQzMGUyMDAxMzY2MDM0ZSIsImF1ZCI6ImNhc3QiLCJpYXQiOjE1OTM2NzY5NjUsImV4cCI6MTU5Mzc2MzM2NSwiYXpwIjoidDVqUHRvcVJkOTY0YmJWbk90V1ZzcHY3WUEzNVB3dmEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIl19.m5VhFc_dp9e98ieVAh8GNG39qN-Q7PocAKA7tW-CqiVksdilnHpMOtVMRGtXi-TIUtfNk57K479bKYBEgMBkoi3RoYoI0ABnU_rBc0xHmvIvfQnClcFmXHemIYbUjj30FwWF8in_GkEHsnEcZ72vHqA-MygRi1gli1dtgBl2aolkfssGbFneIRcjTLG8Y1xttu7nylMpuFfkyvKJ3gmLbGufZl3M6PEM2K8Earhd0Ed2y4IKUR-7stCCHyvbHjHFNiihxuz0hQmXt173-Tf3a-AP5U1I-YkNEUjWeQHIY5pFdxDjcZt-gXOYz6SsnB24anTMW0JTdYbYnweBF2RA8Q",
    "casting_director": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImN5S0NzTE5yS01UblpfTUhjdERTaSJ9.eyJpc3MiOiJodHRwczovL2JlcnJ0YW01MTAudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlZmQ4NTI2YTFmNjAzMDAxOWIwNjg2MyIsImF1ZCI6ImNhc3QiLCJpYXQiOjE1OTM2NzcwMjksImV4cCI6MTU5Mzc2MzQyOSwiYXpwIjoidDVqUHRvcVJkOTY0YmJWbk90V1ZzcHY3WUEzNVB3dmEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphY3RvcnMiLCJkZWxldGU6YWN0b3JzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiXX0.1vDaGbszRDMgwnpEXlRIYy6mC_4CogXb9uRUuiX6jQ1s1zFMKmT7Kq_Z5Dlgn7GrLVNvMlemgHTJ0zj5KcEhY_IKSzZfZ8b-D38buliM5BzunfUPM9X96GLXLcaKOrErtKs0oekN706QiGI21zdl5QX26IOyPilr4PPcQH-OHbRoK4O51sgb873TMwS5drG6aF4XBlzARQt1rWlMcWVgQNga6mhyM7XOb5bIPi_LsDNdYetgvbvQeqdqUgqTrE5YhL4KaTSYw3CtssZgf0kIwOWXd6k2MsnQhr0Lm9r39XqHMwepd7DXmRKP8MR0fFrU3ip8idheGo-bwxEDMYrZ_A",
    "executive_producer": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImN5S0NzTE5yS01UblpfTUhjdERTaSJ9.eyJpc3MiOiJodHRwczovL2JlcnJ0YW01MTAudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlZmEyOWUxNzE0NjhjMDAxM2ZmYjkxZSIsImF1ZCI6ImNhc3QiLCJpYXQiOjE1OTM2NzY5MDcsImV4cCI6MTU5Mzc2MzMwNywiYXpwIjoidDVqUHRvcVJkOTY0YmJWbk90V1ZzcHY3WUEzNVB3dmEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphY3RvcnMiLCJjcmVhdGU6bW92aWVzIiwiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyJdfQ.Av_Qco_PtBSW9GXU5JMswP009BwikY7IGc0lHLjFSeLV6ymWQs34N9cIkEp6VNWrtotdz3gWaEDc_ukLKjxkTAl4sU-lUI-C68QOegvUu5I9m7wGVLfJRXp-BG4ootco-7Z6mYObhpo4LRHmbE3KOMl8HkodFC9cP3Y_RNh0SotDIOiJr6eMkI_l16wRj4CInNgF8tHw0PHMKB0O7F7MtKgVhZh6HONUvZEjffY7eEpiOOHWXsxhVo8WoUfe1LwaSe6aIemhoh_lHTvyeUUHG6PQ-18E04PoeJnfjuBghL75J-DVkIFynuTCCub-GTO-FoMuptChnTPP8HSqdG1lPA"
}

casting_assistant_header = {
    'Authorization': bearer_tokens['casting_assistant']
}

casting_director_header = {
    'Authorization': bearer_tokens['casting_assistant']
}

executive_producer_header = {
    'Authorization': bearer_tokens['casting_assistant']
}


class CastAgencyTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
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

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    DONE
    Write at least one test for each test for successful operation
    and for expected errors.
    """
    def test_get_actors(self):
        res = self.client().get('/actors', headers=casting_assistant_header)
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
        res = self.client().patch('/actors/2', json=update_actor,
                                  headers=casting_director_header)
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
                                  headers=casting_director_header)
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
                                  headers=casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_delete_actors_by_id(self):
        res = self.client().delete('/actors/2',
                                   headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_actor'], 2)

    def test_400_delete_actors_by_id(self):
        res = self.client().delete('/actors/21234',
                                   headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_delete_actors(self):
        res = self.client().delete('/actors/2',
                                   headers=casting_assistant_header)
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
                                 headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['new_actor'] > 0)
        self.assertTrue(len(data['actors']) > 0)

    def test_400_fail_to_add_actors(self):
        new_actor = {
            'name': 'John Smith'
        }

        res = self.client().post('/actors', json=new_actor,
                                 headers=casting_director_header)
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
                                 headers=casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_get_movies(self):
        res = self.client().get('/movies', headers=casting_assistant_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['movies'] > 0)

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
            'release_date': date.today().__str__()
        }

        print(update_movie)
        res = self.client().patch('/movies/2', json=update_movie,
                                  headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['update_movie']) > 0)

    def test_400_fail_to_update_movies(self):
        update_movie = {
            'title': 'John Smith',
            'release_date': date.today()
        }
        res = self.client().patch('/movies/2', json=update_movie,
                                  headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_update_movies(self):
        update_movie = {
            'title': 'John Smith',
            'release_date': date.today()
        }
        res = self.client().patch('/moveis/2', json=update_movie,
                                  headers=casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_delete_movies_by_id(self):
        res = self.client().delete('/movies/2',
                                   headers=executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_movie'], 2)

    def test_400_delete_movies_by_id(self):
        res = self.client().delete('/movies/21234',
                                   headers=executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_delete_movies(self):
        res = self.client().delete('/movies/2',
                                   headers=casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_add_movies(self):
        new_movie = {
            'title': 'Inception 2',
            'release_date': date.today()
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers=executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['new_movie'] > 0)
        self.assertTrue(len(data['movies']) > 0)

    def test_400_fail_to_add_movies(self):
        new_movie = {
            'title': 'Inception 2'
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers=executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_add_movies(self):
        new_movie = {
            'title': 'Inception 2',
            'release_date': date.today()
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
