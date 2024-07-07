# Healthcare Database Project

## Introduction

This project consists of adatabase management system specifically designed for a healthcare app. It utilizes PostgreSQL and Docker for data storage and management, incorporating advanced features such as materialized views and integrity constraints to ensure data accuracy and efficiency.
Furthermore, we also implemented a RESTful API to interact with the database via web requests. You can test the SAUDE Management System API endpoints using Bruno.

### Prerequisites

Make sure you have the following installed:

    Python 3.8 (or more)
    Docker
    PostgreSQL
    Flask
    Bruno
    psycopg2
    psycopg_pool

### Features

   - PostgreSQL Database: Utilizes PostgreSQL for reliable and efficient data management.
  
   - Materialized Views: Enhances query performance by storing the result of a query physically.
   
  Integrity Constraints: Ensures data consistency and reliability with various constraints.
  Flask API: Provides a RESTful API for interacting with the database.
  Docker: Simplifies the setup and deployment process using Docker.

### Getting Started

Clone the repository to your local machine using the following command in your terminal or command prompt:

```bash
git clone https://github.com/guilhermedcampos/saude-database/
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Starting the Workspace

### Running Docker

To open the Jupyter Notebook workspace via Docker Compose, first, navigate to the /bdist-workspace directory in your terminal:

```bash
cd bdist-workspace/
```

Next, start the service with:

```bash
docker compose up
```

The Jupyter Notebook service runs on port 9999 and requires authentication via a token. After starting the service, locate your authentication token in the terminal logs. Look for the section towards the end of the logs that provides a URL with your token, such as http://127.0.0.1:9999/lab?token=YOUR_AUTHENTICATION_TOKEN. Copy and paste this URL into your browser to access the Jupyter Notebook workspace. If needed, you can also view these logs in the Containers tab within the Docker Desktop application.

### Connecting and Populating the Database

Set up the PostgreSQL database with the following commands in the Jupiter Network command line:

```psql
-- Connecting to postgres (must have a postgres user already)
psql -h postgres -U postgres
```

```sql
CREATE USER saude WITH PASSWORD 'saude';
CREATE DATABASE saude WITH OWNER = bank ENCODING = 'UTF8';
GRANT ALL ON DATABASE bank TO bank;

---Now let's populate the database and add it's constraints, tables, triggers and procedures:

\i data/Saude.sql
\i data/populate.sql
```

Now that the database is populated, all SQL queries can be performed on existing data. Alternatively, the folder data also comes with a materialized view "Vista.sql" with the all the appointments and information on them. To run that view do:

```sql
\i data/Vista.sql
```

## App Setup

### Running Docker

Run docker in a terminal once again but instead do the following command: 

```bash
docker compose -f docker-compose.app.yml up
```

Once the Docker containers are running, you can connect to the PostgreSQL database using psql:

```psql
psql -h postgres -U postgres
```

### Running the App

To start the Flask application, run:

```bash
python3 app/app.py
```

The app will be available at http://localhost:5001.


## Testing with BRUNO

You can test the SAUDE Management System API endpoints using BRUNO, aN API testing tool. 

### Install BRUNO

First, create a new collection. Open BRUNO and create a new collection for your SAUDE Management System API tests.

Add Requests: For each API endpoint, add a new request in BRUNO with the appropriate method (GET or POST) and URL. For example:

- For the Get Clinics endpoint, add a GET request to http://localhost:5001/.
- For the Create Consultation endpoint, add a POST request to http://localhost:5001/a/<clinic>/registar/ with the required parameters.

Thirdly, set request parameters. For endpoints that require parameters, such as Create Consultation, set the request parameters in the appropriate section in BRUNO. You can use the Query Params tab for query parameters and the Body tab for request body parameters.

Finally, send requests and view responses. You can verify the functionality of your API by checking the status codes and response data.


### Endpoints Supported 

The python app supports the following api requests. To add more simply edit the app.py code to include more features.

1. Get Clinics

    Endpoint: /
    Method: GET
    Description: Retrieves all clinics.
    Response:

    ```json

    [
      {
        "nome": "Clinic Name",
        "morada": "Clinic Address"
      }
    ]
    ```

2. Get Specializations

    Endpoint: /c/<clinic>/
    Method: GET
    Description: Retrieves all specializations for a specific clinic.
    Response:

    ```json

    [
      {
        "especialidade": "Specialization"
      }
    ]
    ```

3. List Doctors

    Endpoint: /c/<clinic>/<specialization>/
    Method: GET
    Description: Lists all doctors for a specific clinic and specialization.
    Response:

    ```json

    {
      "Doctor Name": [
        ("2024-05-30", "08:00"),
        ("2024-05-31", "08:30"),
        ("2024-06-01", "09:00")
      ]
    }
    ```

4. Create Consultation

    Endpoint: /a/<clinic>/registar/
    Method: POST
    Description: Creates a new consultation.
    Parameters:
        paciente: Patient SSN
        medico: Doctor NIF
        data: Date (YYYY-MM-DD)
        hora: Time (HH
        )
    Response:

    ```json

    {
      "consulta marcada": "2024-05-30 às 08:00 com o médico 123456789 para o paciente 987654321",
      "status": "success"
    }
    ```

5. Cancel Consultation

    Endpoint: /a/<clinic>/cancelar/
    Method: POST
    Description: Cancels an existing consultation.
    Parameters:
        paciente: Patient SSN
        medico: Doctor NIF
        data: Date (YYYY-MM-DD)
        hora: Time (HH
        )
    Response:

    ```json

    {
      "consulta cancelada": "2024-05-30 às 08:00 com o médico 123456789 para o paciente 987654321",
      "status": "success"
    }
    ```

BRUNO provides a user-friendly interface for testing and debugging your API, making it easier to ensure your endpoints are working as expected

