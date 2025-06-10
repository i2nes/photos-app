# Project XPTO

This is a Django project running with Docker and Qdrant for vector embeddings.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd project_xpto
    ```

2.  **Build and create the initial Django project:**
    * Build the Docker images and start the services.
        ```bash
        docker-compose up --build -d
        ```
    * Execute the `startproject` command inside the `web` container to create the Django project files.
        ```bash
        docker-compose exec web django-admin startproject config .
        ```
    * Set the correct file ownership after running the command as root inside the container.
        ```bash
        sudo chown -R $USER:$USER .
        ```
    * You can now stop the containers.
        ```bash
        docker-compose down
        ```

---

## Running the Project

To start the development server:

1.  **Start all services:**
    * To run the containers in the foreground and see live logs:
        ```bash
        docker-compose up
        ```
    * To run the containers in the background (detached mode):
        ```bash
        docker-compose up -d
        ```

2.  **Stop all services:**
    * If running in the foreground, press `Ctrl+C`.
    * If running in the background, or to stop and remove the containers:
        ```bash
        docker-compose down
        ```

---

## Common Commands

All Django `manage.py` commands should be run inside the `web` container.

* **Create migrations:**
    ```bash
    docker-compose exec web python manage.py makemigrations
    ```

* **Apply migrations:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

* **Create a superuser:**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

* **Open the Django shell:**
    ```bash
    docker-compose exec web python manage.py shell
    ```

* **Run tests:**
    ```bash
    docker-compose exec web python manage.py test
    ```

* **View logs:**
    * To view the logs for all services:
        ```bash
        docker-compose logs -f
        ```
    * To view the logs for a specific service (e.g., `web`):
        ```bash
        docker-compose logs -f web
        ```

---

## Services

This project is composed of two main services defined in `compose.yaml`:

* **`web`**: The Django application.
    * Accessible at <http://localhost:8000>
* **`qdrant`**: The Qdrant vector database service.
    * Accessible at <http://localhost:6333>