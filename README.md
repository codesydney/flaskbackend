# flaskbackend

Flask API - skeleton to get started with creating API's in Flask

### Prerequisites

1. Flask
2. MySQL (recommended)

### Instructions

1. Clone this repo
2. python -m venv env
3. pip install -r requirements
4. Fill in .env with your DB values
5. MySQL create schema
6. Use Flask Migrate to create the tables
flask db init
flask db migrate -m "init"
flask db upgrad
7. Use SQL to insert values in Role table - see sql.sql
8. Activate your virtual environment (there is a runenv.bat file for Windows users)
9. flask run
10. Test out the API
For example you can create an admin user using the api/users POST endpoint
