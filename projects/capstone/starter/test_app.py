
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Actor, Movie, db_drop_and_create_all
from datetime import date

casting_assistant_header = {
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImN5S0NzTE5yS01UblpfTUhjdERTaSJ9.eyJpc3MiOiJodHRwczovL2JlcnJ0YW01MTAudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlZmEyYTBkZmQzMGUyMDAxMzY2MDM0ZSIsImF1ZCI6ImNhc3QiLCJpYXQiOjE1OTQwMTU5NjEsImV4cCI6MTU5NDEwMjM2MSwiYXpwIjoidDVqUHRvcVJkOTY0YmJWbk90V1ZzcHY3WUEzNVB3dmEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIl19.2ZFMPDFs0VzQw3UW2iG_8P5bmfGOnXW1cPI_YR898UcM5ns894QB6pI9h1M37B0TFTZKUbEGncBy9l-IIARy0_A0SthVWINEG5GNXCVFXQgE5hyi76jgGrjv3wrQbTRGLew-IenzXPjNPB_e3wewFtx6Wul_x90xXHSWfzYXtDThmi6jFj9KrTvaBTqoL3j6IvynIpXT1KhEJEqyrfxBQYF5grXa-V_QpMevr5Qnd_2sNfWstv5vKwWND1kvJErrva_MsjOhWWx4OQ4yhNWbwuy9ISmIPjcd42WoGXI9LjepU18uJWkDPplovuqyMYeqHIyP6Np2fz2sgFm3jwoiTg'
}

casting_director_header = {
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImN5S0NzTE5yS01UblpfTUhjdERTaSJ9.eyJpc3MiOiJodHRwczovL2JlcnJ0YW01MTAudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlZmQ4NTI2YTFmNjAzMDAxOWIwNjg2MyIsImF1ZCI6ImNhc3QiLCJpYXQiOjE1OTQwMTYwMDcsImV4cCI6MTU5NDEwMjQwNywiYXpwIjoidDVqUHRvcVJkOTY0YmJWbk90V1ZzcHY3WUEzNVB3dmEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphY3RvcnMiLCJkZWxldGU6YWN0b3JzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiXX0.bEK1LWS5APqukYNx9hXvTThPD9n4Felq_Io803IfZRMy2Ua4UZBL2T_er12TYKp4_c7JbAWXQRF5lF_9ujzoutJf-qibLpWVvHoh2Zt2szr8FDrrBmBp2f7ul9UEyGIekioRYrn0nGrfAU-DbNwyPmjFV9WWuBYYdDtOkjB-TenlbVVD9FeP1QPExomVzhSUpzG6l0Yzjho-G_5yGnpZteh49QbNRhnJh0JP8qFu6ptyUrw_0z3EwJ4gBgR-SSHqlFv7UHc9V_esZ-9MQvgqWUy8MeLDpWqoRzcXpKhz4R9vfPRVU1LsJW-5Zzl7em7at3mAjX3HKpcH8Gq-aWTiFw'
}

executive_producer_header = {
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImN5S0NzTE5yS01UblpfTUhjdERTaSJ9.eyJpc3MiOiJodHRwczovL2JlcnJ0YW01MTAudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlZmEyOWUxNzE0NjhjMDAxM2ZmYjkxZSIsImF1ZCI6ImNhc3QiLCJpYXQiOjE1OTQwMTU3MDgsImV4cCI6MTU5NDEwMjEwOCwiYXpwIjoidDVqUHRvcVJkOTY0YmJWbk90V1ZzcHY3WUEzNVB3dmEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTphY3RvcnMiLCJjcmVhdGU6bW92aWVzIiwiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyJdfQ.rH-Wsc4ecAKlQXzo8BlB2No-Q02m82X7yeSIOL-lsW0mJ0RxufTB4woOyd0zx31VuACzzxOAsvtg1knhWgugIkoFqy6OYzFjFWw-GXmzQNCx978_bG3igqUjGMy0qpteqFiCHzVDZapQiPhWkcrNNsSi_sehvQwENOudZEZDvDZTI07rOFy7OMB_mUckOvLC_KcqpRE1vdyXykBfscqyugA_nuQ1CeRpCxcdlEp_kP1YeJe6OK6NytqJ_tUg7-Wnd5QKN9sEnI4vugj-BXl_moSpLTedND5D5UnNpC1O62hwLvcsIb2pJGXZToCYmXBnGZ7IRG9sklNYqk-2bsVjZQ'
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

        new_actor = {
            'name': 'Test Name',
            'age': 25,
            'gender': 'Male'
        }

        res = self.client().post('/actors', json=new_actor,
                                 headers=casting_director_header)

        new_movie = {
            'title': 'Test Movie',
            'release_date': '2020-06-17'
        }

        res = self.client().post('/movies', json=new_movie,
                                 headers=executive_producer_header)

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
        res = self.client().patch('/actors/1', json=update_actor,
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
        res = self.client().delete('/actors/1',
                                   headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_actor'], 1)

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
        self.assertTrue(data['actors'] > 0)

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
                                  headers=casting_director_header)
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
                                  headers=casting_director_header)
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
                                  headers=casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')

    def test_delete_movies_by_id(self):
        res = self.client().delete('/movies/1',
                                   headers=executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_movie'], 1)

    def test_400_delete_movies_by_id(self):
        res = self.client().delete('/movies/21234',
                                   headers=executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_401_fail_to_delete_movies(self):
        res = self.client().delete('/movies/1',
                                   headers=casting_assistant_header)
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
                                 headers=executive_producer_header)
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
                                 headers=executive_producer_header)
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
                                 headers=casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'authentification failed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
