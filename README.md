
---

# 📊 **Dynamic Report Generator Service**

Welcome to the **Dynamic Report Generator**, a microservice crafted using Django to simplify large-scale CSV data processing. This service empowers users to upload datasets, define transformation logic through JSON/YAML rules, and generate insightful reports—either on-demand or via scheduled tasks. Background processing is seamlessly handled by Celery with Redis as the broker, ensuring smooth performance even for heavy workloads.

---

## ⚡️ **Core Capabilities**

- 📂 Upload CSV datasets (input & reference files)
- ⚙️ Define custom transformation rules using JSON or YAML
- 🚀 Trigger instant report generation through RESTful APIs
- 📥 Securely download generated reports in CSV format
- ⏰ Automate report generation using cron-based schedules
- 🔒 Enforced JWT authentication across all endpoints
- 🛠️ Powered by DRF, Celery, Redis, and Docker for scalability

---

## 🛠️ **Technology Overview**

This service leverages a modern, containerized architecture designed for scalability, maintainability, and ease of deployment.

| **Component**      | **Technology Stack**                 |
|--------------------|--------------------------------------|
| Programming Lang.  | Python 3.11                          |
| Web Framework      | Django 4.x + Django REST Framework   |
| Background Tasks   | Celery                               |
| Task Broker        | Redis                                |
| Scheduling         | django-celery-beat (Cron Jobs)       |
| Authentication     | JWT via `djangorestframework-simplejwt` |
| Database (Optional)| PostgreSQL                           |
| Containerization   | Docker & Docker Compose              |
| Testing            | Django TestCase + DRF APITestCase    |

---

## 🌐 **Service Blueprint**

Visualizing how components interact within the system:

```
+-------------+          API Requests          +--------------------+
|   CLIENT    |  ───────────────────────────▶  |   Django + DRF     |
+-------------+                                +--------------------+
                                                      │
                                                      ▼
                                        +------------------------+
                                        |   Redis (Task Broker)  |
                                        +------------------------+
                                                      │
                                                      ▼
                                             +----------------+
                                             |   Celery Worker |
                                             +----------------+
                                                      │
                                                      ▼
                                         +-----------------------+
                                         |   File Transformation |
                                         +-----------------------+
                                                      │
                                                      ▼
                                            +-----------------+
                                            |  Report Output  |
                                            +-----------------+
```

---

## 📂 **Project Setup Guide**

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/PrabhatTheCoder/natwest_assignment.git
cd natwest_assignment
```

### 2️⃣ (Optional) Setup Virtual Environment
> While Docker handles isolation, for local Python tasks:
```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
# OR
venv\Scripts\activate     # For Windows
```

### 3️⃣ Launch Services via Docker
```bash
docker-compose up --build
```

### 4️⃣ Running Tests with Coverage
Ensure containers are active, then execute:
```bash
docker-compose run web sh -c "coverage erase && coverage run manage.py test && coverage html && coverage report"
```

---

## 🔑 **Authentication Workflow**

All API endpoints are secured with **JWT tokens**. Obtain tokens via registration or login.

- **Base URL:** `http://0.0.0.0:8000/api/`

### ▶️ Register
```http
POST /auth/register/
```
Payload:
```json
{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword"
}
```

### ▶️ Login
```http
POST /auth/login/
```
Payload:
```json
{
    "email": "user@example.com",
    "password": "securepassword"
}
```

Both responses return:
- `access` token
- `refresh` token

Use:
```bash
-H "Authorization: Bearer <access_token>"
```

### ▶️ Token Refresh
```bash
curl -X POST http://0.0.0.0:8000/api/auth/refresh/ \
-d '{"refresh": "<refresh_token>"}' \
-H "Content-Type: application/json"
```

### ▶️ Logout
```http
GET /auth/logout/
```

---

## 📤 **File Management APIs**

Upload necessary files before generating reports.

### 🔹 Upload Transformation Rules
```http
POST /upload-rules/
```
Example:
```bash
curl -X POST http://0.0.0.0:8000/api/upload-rules/ \
-F "file=@/path/to/rules.json"
```

---

### 🔹 Upload CSV Files
```http
POST /upload-files/
```
Example:
```bash
curl -X POST http://0.0.0.0:8000/api/upload-files/ \
-F "input=@/path/to/input.csv" \
-F "reference=@/path/to/reference.csv"
```

---

## ⚡ **Report Lifecycle**

### 🚀 Trigger Report Generation
```http
POST /generate-report/
```
Example:
```bash
curl -X POST http://0.0.0.0:8000/api/generate-report/ \
-H "Authorization: Bearer <access_token>" \
-F "input=@/path/to/input.csv" \
-F "reference=@/path/to/reference.csv"
```
Response:
```json
{
    "task_id": "abc123-task-id"
}
```

Track this `task_id` for asynchronous processing status.

---

### 📥 Download Generated Report
```http
GET /download-report-view/
```
Example:
```bash
curl -X GET http://0.0.0.0:8000/api/download-report-view/ \
-H "Authorization: Bearer <access_token>"
```
Returns CSV data in response body.

---

## ⏲️ **Automated Report Scheduling**

Define periodic jobs using cron expressions.

### Schedule a Report
```http
POST /trigger-scheduled-report/
```
Example:
```bash
curl -X POST http://0.0.0.0:8000/api/trigger-scheduled-report/ \
-H "Authorization: Bearer <access_token>" \
-F "input_file=@/path/to/input.csv" \
-F "reference_file=@/path/to/reference.csv" \
-F "rules_file=@/path/to/rules.json" \
-F "cron=*/10 * * * *"
```
This will auto-trigger report generation every 10 minutes.

---

## 🚨 **Error Handling Guide**

| **HTTP Code** | **Meaning**                      |
|---------------|-----------------------------------|
| 400           | Invalid input or missing data     |
| 401           | Authentication failure            |
| 404           | Resource not found                |
| 500           | Internal server error             |

Ensure valid tokens and correct file formats to avoid common issues.

---

## 📎 **Resources & Tools**

- **Example Files:** [Google Drive Link](https://drive.google.com/drive/folders/1CT6r7pEOywQODt2XgZgBb5-ZQNjmB7en?usp=drive_link)
- **Postman Collection:** [Access Here](https://survey-quiz.postman.co/workspace/Team-Workspace~0e64a07b-e68d-43f5-83f3-428269c455a1/collection/34406608-524d8bb9-971e-4230-a585-3f18338e6c7d?action=share&creator=34406608&active-environment=34406608-661818f6-2565-4bad-89f2-7df328911bd8)

---

## 🚧 **Example Usage**

### ▶️ User Registration
```bash
curl -X POST http://0.0.0.0:8000/api/auth/register/ \
-d '{"email": "user@example.com", "name": "User", "password": "pass123"}' \
-H "Content-Type: application/json"
```

### ▶️ Quick Report Trigger
```bash
curl -X POST http://0.0.0.0:8000/api/generate-report/ \
-H "Authorization: Bearer <access_token>" \
-F "input=@input.csv" \
-F "reference=@reference.csv"
```

---

## 🎯 **Summary**

This microservice is tailored for teams and organizations needing robust, flexible, and automated data reporting solutions. Whether processing large datasets or automating periodic report generation, this service ensures secure, scalable, and efficient handling of your reporting workflows.

For any issues, contributions, or feature requests, feel free to fork the repository or raise an issue!

---

