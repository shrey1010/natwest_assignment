# 🧾 Report Generator Microservice

This Django-based microservice allows users to upload large CSV files and generate transformation-based reports using configurable rules defined in JSON or YAML format. It supports on-demand as well as scheduled (cron-based) report generation and is built with Celery for background processing and Redis as a task queue.

---

## 🚀 Features

- Upload input and reference CSV files
- Upload transformation rules in JSON/YAML
- Trigger report generation via API
- Download generated report
- Schedule periodic report generation using cron syntax
- JWT authentication required for all endpoints
- Built with Django REST Framework, Celery, Redis, and Docker

---

## 🧱 Tech Stack

- Django + Django REST Framework
- Celery + Redis
- Django-Celery-Beat
- Docker + Docker Compose
- PostgreSQL (optional, depending on persistence needs)

---


## 🧱 Tech Stack

| Category        | Technology                        |
|----------------|------------------------------------|
| Language        | Python 3.11                        |
| Web Framework   | Django 4.x + Django REST Framework |
| Task Queue      | Celery                             |
| Broker          | Redis                              |
| Database        | PostgreSQL                         |
| Auth            | JWT (via djangorestframework-simplejwt) |
| Cron Scheduling | django-celery-beat                 |
| Containerization| Docker & Docker Compose            |
| Testing         | Django TestCase + DRF APITestCase  |

---

## Example Files

You can find example input, reference, and rules files in this Google Drive folder:

[Example Files](https://drive.google.com/drive/folders/1CT6r7pEOywQODt2XgZgBb5-ZQNjmB7en?usp=drive_link)

## You can find the Postman collection for this API here:

[Postman Collection](https://survey-quiz.postman.co/workspace/Team-Workspace~0e64a07b-e68d-43f5-83f3-428269c455a1/collection/34406608-524d8bb9-971e-4230-a585-3f18338e6c7d?action=share&creator=34406608&active-environment=34406608-661818f6-2565-4bad-89f2-7df328911bd8)


---

## 🏗️ Architecture

```text
             ┌─────────────┐
             │   Client    │
             └─────┬───────┘
                   │
         ┌─────────▼─────────────┐
         │    Django REST API    │
         └─────────┬─────────────┘
                   │
      ┌────────────▼─────────────┐
      │        Celery Queue      │◄────Scheduled Tasks (Celery Beat)
      └────────────┬─────────────┘
                   │
             ┌─────▼─────┐
             │  Worker   │
             └─────┬─────┘
                   │
         ┌─────────▼────────┐
         │ File Processing  │
         └─────────┬────────┘
                   │
         ┌─────────▼────────┐
         │  Report Output   │
         └──────────────────┘



## 📦 Setup

1. **Clone the repository**

```bash
git clone https://github.com/PrabhatTheCoder/natwest_assignment.git
cd natwest_assignment

2. Run the Application (Dockerized)

* **Virtual Environment Creation:**
    * I added step 2, which instructs users to create a virtual environment. This is a best practice for Python projects to isolate dependencies.
    * The commands `python3 -m venv venv` creates a virtual environment named `venv`.
    * `source venv/bin/activate` activates the virtual environment on Linux/macOS.
    * `venv\Scripts\activate` activates the virtual environment on Windows.
    * I placed the virtual environment creation step before the Docker setup, as it's a common practice to set up the Python environment first.

```bash
docker-compose up --build

3.Run Tests inside Docker

After running the application, use the command below to run tests with coverage inside the container (you can do it in another terminal but only after running the application):
```bash
docker-compose run web sh -c "coverage erase && coverage run manage.py test && coverage html && coverage report"

4. 

All endpoints are prefixed with this base URL.
The base URL for the API is:

http://0.0.0.0:8000/api/


---
Authentication
The API uses token-based authentication. After successful registration or login, a user receives an access token which must be included in the Authorization header for subsequent API requests.

User Registration
Endpoint: POST /auth/register/

Registers a new user.

Request Body:
JSON

{
    "email": "prabhat.patel9134@gmail.com",
    "name": "Prabhat",
    "password": "abc123"
}
Response:

JSON

{
    "user": {
        "id": "38ff7a36-f927-401b-b21b-8bb73de886e6",
        "email": "prabhat.patel9134@gmail.com",
        "name": "Prabhat",
        "phone_number": null
    },
    "access": "access_token",
    "refresh": "refresh_token"
}
User Login
Endpoint: POST /auth/login/

Logs in an existing user and returns authentication tokens.

Request Body:
JSON

{
    "email": "prabhat.patel@gmail.com",
    "password": "abc123"
}
Response:

JSON

{
    "user": {
        "email": "prabhat.patel9134@gmail.com",
        "name": "Prabhat"
    },
    "access": "access_token",
    "refresh": "refresh_token"
}
User Logout
Endpoint: GET /auth/logout/

Logs out the user by invalidating the access token.

Response:

JSON

{
    "message": "Successfully logged out."
}
File Upload
The service allows you to upload files for rule configuration, input data, and reference data.

Upload Rules File
Endpoint: POST /upload-rules/

Uploads the transformation rules file (JSON format).

Request:

Bash

curl -X POST [http://0.0.0.0:8000/api/upload-rules/](http://0.0.0.0:8000/api/upload-rules/) \
-F "file=@/path/to/rules.json"
Response:

JSON

{
    "message": "Rules file uploaded and saved as rules.json"
}
Upload Input and Reference Files
Endpoint: POST /upload-files/

Uploads the input and reference CSV files for report generation.

Request:

Bash

curl -X POST [http://0.0.0.0:8000/api/upload-files/](http://0.0.0.0:8000/api/upload-files/) \
-F "input=@/path/to/input.csv" \
-F "reference=@/path/to/reference.csv"
Response:

JSON

{
    "message": "Input and reference files uploaded successfully."
}
Report Generation
Once the input data, reference data, and rules are uploaded, you can generate a report.

Generate Report
Endpoint: POST /generate-report/

Generates a report based on the provided input and reference files.

Request:

Bash

curl -X POST [http://0.0.0.0:8000/api/generate-report/](http://0.0.0.0:8000/api/generate-report/) \
-H "Authorization: Bearer <access_token>" \
-F "input=@/path/to/input.csv" \
-F "reference=@/path/to/reference.csv"
Response:

JSON

{
    "task_id": "unique_task_id"
}
This task ID can be used to track the status of the report generation.

Download Report
Endpoint: GET /download-report-view/

Downloads the generated report once it's ready.

Request:

Bash

curl -X GET [http://0.0.0.0:8000/api/download-report-view/](http://0.0.0.0:8000/api/download-report-view/) \
-H "Authorization: Bearer <access_token>"
Response:

JSON

{
    "body": "outfield1,outfield2,outfield3,...\nJohnSmith,Alpha,A1B1,...\n"
}
The response will contain the report data in CSV format.

Scheduled Report Generation
The service also supports triggering report generation on a scheduled basis using cron expressions.

Trigger Scheduled Report
Endpoint: POST /trigger-scheduled-report/

Schedules a report generation at a specific interval.

Request:

Bash

curl -X POST [http://0.0.0.0:8000/api/trigger-scheduled-report/](http://0.0.0.0:8000/api/trigger-scheduled-report/) \
-H "Authorization: Bearer <access_token>" \
-F "input_file=@/path/to/input.csv" \
-F "reference_file=@/path/to/reference.csv" \
-F "rules_file=@/path/to/rules.json" \
-F "cron=*/5 * * * *"
Response:

JSON

{
    "message": "Scheduled report triggered."
}
Error Handling
Here are the common error responses you may encounter:

400 Bad Request: Invalid request parameters or missing required fields.
401 Unauthorized: Missing or invalid authentication token.
404 Not Found: The requested resource was not found.
500 Internal Server Error: An unexpected server error occurred.
Authentication (continued)
Access Token: This token is used to authenticate API requests. It should be included in the Authorization header as follows:

Bash

-H "Authorization: Bearer <access_token>"
Refresh Token: This token can be used to obtain a new access_token when it expires.

Example of refreshing the access token:

Bash

curl -X POST [http://0.0.0.0:8000/api/auth/refresh/](http://0.0.0.0:8000/api/auth/refresh/) \
-H "Content-Type: application/json" \
-d '{"refresh": "<refresh_token>"}'
Example Requests
Register a User
Bash

curl -X POST [http://0.0.0.0:8000/api/auth/register/](http://0.0.0.0:8000/api/auth/register/) \
-H "Content-Type: application/json" \
-d '{"email": "prabhat.patel9134@gmail.com", "name": "Prabhat", "password": "abc123"}'
Generate a Report
Bash

curl -X POST [http://0.0.0.0:8000/api/generate-report/](http://0.0.0.0:8000/api/generate-report/) \
-H "Authorization: Bearer <access_token>" \
-F "input=@/path/to/input.csv" \
-F "reference=@/path/to/reference.csv"

curl -X POST http://0.0.0.0:8000/api/auth/get-access-token/ \
-H "Content-Type: application/json" \
-d '{"refresh": "refresh_Code"}'


Conclusion
This API allows you to manage file uploads, generate reports, and schedule reports efficiently. It is designed for users who need to process and transform large datasets into structured reports with customizable transformation rules. Authentication is provided via token-based systems, ensuring secure access to all endpoints.

