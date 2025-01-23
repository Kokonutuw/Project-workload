# Project Workload Management System

A Django-based workload management system designed to help track and manage project tasks and resources efficiently.

## Features

- Task and workload management
- Resource allocation tracking
- Data import/export functionality
- Interactive charts and visualizations
- JIRA integration
- User-friendly interface with autocomplete features

## Tech Stack

- Python 3.x
- Django 4.2.1
- Django Import/Export
- Chart.js
- JIRA API integration
- SQLite database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Kokonutuw/Project-workload.git
cd Project-workload
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r workload/requirements.txt
```

4. Run migrations:
```bash
cd workload
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

- `/workload` - Main project directory
  - `/templates` - HTML templates
  - `/workloadApp` - Core application logic
  - `/management` - Custom management commands
  - `/export_files` - Export file storage

## Dependencies

Key dependencies include:
- Django 4.2.1
- django-import-export 3.2.0
- django-autocomplete-light 3.9.7
- JIRA 3.5.1
- Chart.js 1.2

For a complete list of dependencies, see `workload/requirements.txt`.

