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

### Starting the Workspace

To open the Jupyter Notebook workspace via Docker Compose, first, navigate to the /bdist-workspace directory in your terminal:

```bash
cd bdist-workspace/
```

Next, start the service with:

```bash
docker compose up
```

The Jupyter Notebook service runs on port 9999 and requires authentication via a token. After starting the service, locate your authentication token in the terminal logs. Look for the section towards the end of the logs that provides a URL with your token, such as http://127.0.0.1:9999/lab?token=YOUR_AUTHENTICATION_TOKEN. Copy and paste this URL into your browser to access the Jupyter Notebook workspace. If needed, you can also view these logs in the Containers tab within the Docker Desktop application.


Set up the PostgreSQL database using the provided schema:

sql

    -- Example: Execute this in your PostgreSQL client
    CREATE DATABASE saude;
    \c saude
    \i schema.sql

Configuration

Set the DATABASE_URL environment variable to point to your PostgreSQL instance. For example:

bash

export DATABASE_URL="postgres://username:password@hostname/saude"

Docker Setup

    Ensure Docker is installed on your system. If not, download and install Docker from the official website.

    Start the PostgreSQL database using Docker Compose:

    bash

docker compose -f docker-compose.app.yml up

Once the Docker containers are running, you can connect to the PostgreSQL database using psql:

bash

    psql -h postgres -U postgres

Usage

To start the Flask application, run:

bash

python app.py

The app will be available at http://localhost:5001.
API Endpoints
Get Clinics

    Endpoint: /
    Method: GET
    Description: Retrieves all clinics.
    Response:

    json

    [
      {
        "nome": "Clinic Name",
        "morada": "Clinic Address"
      }
    ]

Get Specializations

    Endpoint: /c/<clinic>/
    Method: GET
    Description: Retrieves all specializations for a specific clinic.
    Response:

    json

    [
      {
        "especialidade": "Specialization"
      }
    ]

List Doctors

    Endpoint: /c/<clinic>/<specialization>/
    Method: GET
    Description: Lists all doctors for a specific clinic and specialization.
    Response:

    json

    {
      "Doctor Name": [
        ("2024-05-30", "08:00"),
        ("2024-05-31", "08:30"),
        ("2024-06-01", "09:00")
      ]
    }

Create Consultation

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

    json

    {
      "consulta marcada": "2024-05-30 às 08:00 com o médico 123456789 para o paciente 987654321",
      "status": "success"
    }

Cancel Consultation

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

    json

    {
      "consulta cancelada": "2024-05-30 às 08:00 com o médico 123456789 para o paciente 987654321",
      "status": "success"
    }

Ping

    Endpoint: /ping
    Method: GET
    Description: Simple endpoint to check if the server is running.
    Response:

    json

    {
      "message": "pong!",
      "status": "success"
    }

Testing with BRUNO

You can test the SAUDE Management System API endpoints using BRUNO, a powerful API testing tool. Here's how:

    Install BRUNO: Follow the instructions on the BRUNO website to install BRUNO.

    Create a New Collection: Open BRUNO and create a new collection for your SAUDE Management System API tests.

    Add Requests: For each API endpoint, add a new request in BRUNO with the appropriate method (GET or POST) and URL. For example:
        For the Get Clinics endpoint, add a GET request to http://localhost:5001/.
        For the Create Consultation endpoint, add a POST request to http://localhost:5001/a/<clinic>/registar/ with the required parameters.

    Set Request Parameters: For endpoints that require parameters, such as Create Consultation, set the request parameters in the appropriate section in BRUNO. You can use the Query Params tab for query parameters and the Body tab for request body parameters.

    Send Requests and View Responses: Send the requests and view the responses in BRUNO. You can verify the functionality of your API by checking the status codes and response data.

    Automate Tests: BRUNO allows you to create automated tests by setting up test scripts in the Tests tab. You can write JavaScript code to validate the response data and status codes.

BRUNO provides a user-friendly interface for testing and debugging your API, making it easier to ensure your endpoints are working as expected

