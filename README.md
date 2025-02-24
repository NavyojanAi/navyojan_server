# Project Title

## Description
This repository contains the backend codebase for scholarships application, which fetches scholarship data from www.wemakescholars.com, delivering final insights on particular stocks. It utilizes Azure OpenAI for the copilot feature. It is built using Django and Django REST Framework (DRF) to provide a robust and scalable API for managing application data.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Aura-Tech-India/backend.git
   ```

2. Trigger docker to start the whole server:
   ```bash
   docker compose up -d --build
   ```

## Usage
- Access the application at `http://127.0.0.1:8080/`.
- Use the Django admin panel at `http://127.0.0.1:8080/admin/` to manage the data.
