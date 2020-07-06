# Full Stack Capstone Project

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Accessing API Endpoints from Heroku
The application has been fully deployed on Heroku: https://casting-agency-wu.herokuapp.com/
You can access all the API endpoints mentioned in the API Documents below with the domain provided above.

### Auth0
To test the API Endpoints on Heroku, you'll also need the JWT tokens from Auth0 authorization process.
You can find the existing bearer tokens for each role from `models.py`, or using the Auth0 login page below:
https://berrtam510.us.auth0.com/authorize?audience=cast&response_type=token&client_id=t5jPtoqRd964bbVnOtWVspv7YA35Pwva&redirect_uri=https://casting-agency-wu.herokuapp.com/

Use the following login:
- Casting Assistant: casting.assistant@hotmail.com, Password: Udacity2020
- Casting Director: casting.director@hotmail.com, Password: Udacity2020
- Executive Producer: executive.producer@hotmail.com, Password: Udacity2020

## Running the server
To run the server locally, make sure to change the `datapath` variable to `localhost:5432`(the commented out one), and then execute:

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Testing
To run the tests, run
```
dropdb cast_agency_test
createdb cast_agency_test
python test_app.py
```

## API Reference

### Getting Started

* Base URL: This app is currently hosted on Heroku: https://casting-agency-wu.herokuapp.com/. You can use this domain for your frontend configuration.
* Authentication: Please refer to the "Accessing API Endpoints from Heroku" section for authentication information.

### Error Handling

Errors are returned as JSON objects in the following format:<br>

    {
        "success": False,
        "error": 404,
        "message": "resource not found"
    }

The API will return three error types:

* 400 – Bad Request
* 401 – Authorization Failed
* 404 – Resource Not Found
* 405 – Method Not Allowed
* 422 – Unprocessable
* 500 – Internal Server Error

### Endpoints

#### GET /actors
* General: Returns the list of all actors.
* Request Arguments: None.
* Required Permission: `get:actors`
* Sample: `curl https://casting-agency-wu.herokuapp.com/actors`<br>

        {
            "actors": [
                {
                    "age": 25,
                    "gender": "Male",
                    "id": 1,
                    "name": "John Smith"
                }
            ], 
            "success": true
        }

#### GET /movies
* General: Returns the list of all movies.
* Request Arguments: None.
* Required Permission: `get:movies`
* Sample: `curl https://casting-agency-wu.herokuapp.com/movies`<br>

        {
            "movies": [
                {
                    "id": 1,
                    "release_date": "2020-06-17",
                    "title": "John Wick"
                }
            ],
            "success": true
        }

#### DELETE /actors/\<int:actor_id\>
* General:
  * Deletes an actor from the database by actor_id.
  * Returns the deleted actor id if successful.
* Request Arguments: None.
* Required Permission: `delete:actors`
* Sample: `curl https://casting-agency-wu.herokuapp.com/actors/1 -X DELETE`<br>

        {
            "deleted": 1, 
            "success": true
        }

#### DELETE /movies/\<int:movie_id\>
* General:
  * Deletes a movie from the database by movie_id.
  * Returns the deleted movie id if successful.
* Request Arguments: None.
* Required Permission: `delete:movies`
* Sample: `curl https://casting-agency-wu.herokuapp.com/movies/1 -X DELETE`<br>

        {
            "deleted": 1, 
            "success": true
        }

#### POST /actors
* General:
  * Add a new actor to the database with JSON request parameters.
  * Returns the new actor id and the total number of actors if successful.
* Request Arguments: a JSON object containing request parameters(See example).
* Required Permission: `create:actors`
* Sample: `curl https://casting-agency-wu.herokuapp.com/actors -X POST -H "Content-Type: application/json" -d '
        {
            "name": "Carry Underwood",
            "gender": "Female",
            "age": 24
        }'`<br>

        {
            "actors": 12,
            "new_actor": 10,
            "success": true
        }

#### POST /movies
* General:
  * Add a new movie to the database with JSON request parameters.
  * Returns the new movie id and the total number of movies if successful.
* Request Arguments: a JSON object containing request parameters(See example).
* Required Permission: `create:movies`
* Sample: `curl https://casting-agency-wu.herokuapp.com/movies -X POST -H "Content-Type: application/json" -d '
        {
            "title": "Inception 2",
            "release_date": "2020-06-17"
        }'`<br>

        {
            "movies": 3,
            "new_movie": 3,
            "success": true
        }


#### PATCH /actors\<int:actor_id\>
* General:
  * Modify an actor data from the database by actor_id with JSON request parameters.
  * Returns the updated actor id if successful.
* Request Arguments: a JSON object containing request parameters(See example).
* Required Permission: `patch:actors`
* Sample: `curl https://casting-agency-wu.herokuapp.com/actors/3 -X POST -H "Content-Type: application/json" -d '
        {
            "name": "Nicole Kidman",
            "gender": "Female",
            "age": 53
        }'`<br>

        {
            "success": true,
            "update_actor": [
                {
                    "age": 53,
                    "gender": "Female",
                    "id": 3,
                    "name": "Nicole Kidman"
                }
            ]
        }

#### PATCH /movies\<int:movie_id\>
* General:
  * Modify a movie data from the database by movie_id with JSON request parameters.
  * Returns the updated movie id if successfuls.
* Request Arguments: a JSON object containing request parameters(See example).
* Required Permission: `patch:movies`
* Sample: `curl https://casting-agency-wu.herokuapp.com/movies/3 -X POST -H "Content-Type: application/json" -d '
        {
            "title": "Inception 3"
        }'`<br>

        {
            "success": true,
            "update_movie": [
                {
                    "title": "Inception 3",
                    "release_date": "2020-06-17"
                }
            ]
        }

