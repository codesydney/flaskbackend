# flaskbackend

Flask API - skeleton to get started with creating API's in Flask

### Prerequisites

1. Flask
2. MySQL
3. Sendgrid

### Instructions

1. Clone this repo
2. python -m venv env
3. pip install -r requirements
4. Fill in .env with your DB values
5. MySQL create schema
6. Use Flask Migrate to create the tables
* flask db init
* flask db migrate -m "init"
* flask db upgrade
7. Use SQL to insert values in Role table - see sql.sql
8. Activate your virtual environment (there is a runenv.bat file for Windows users)
9. flask run
10. Test out the API
* For example you can create an admin user using the api/users POST endpoint

### Features

1. Endpoint to create User (admin)
2. Endpoints to create, update, delete, Customer - 1:1 linked to User
3. Endpoints to create, update, delete, get Inventory - Not linked to any other table
4. User login
5. Forgot and reset password
6. Uses Sendgrid to send email
7. Pagination for any GET endpoint
8. Swagger - need to manually edit YAML file (export to JSON)
* Access swagger via /swagger
