# StudyBridge Germany

StudyBridge Germany is a full-stack platform for an international student consultancy based in Germany. It will bring the public website, student application portal, and business administration tools together.

## Technology

- Python 3.11+
- Django Templates and Bootstrap 5
- Microsoft SQL Server with `mssql-django`
- Git and GitHub

## Local development

From the project directory, create and activate a virtual environment, then install the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, generate a unique `DJANGO_SECRET_KEY`, and fill in the SQL Server connection values. Do not commit `.env` or real credentials. The configured database backend uses the installed ODBC Driver 17 for SQL Server.

Run Django's configuration checks with:

```powershell
python manage.py check
python manage.py runserver
```

Database migrations require a running SQL Server and valid connection settings:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

The current local SQL Server instance is `SQLEXPRESS`. Before running database-backed features, set `DB_HOST=localhost\SQLEXPRESS`, leave `DB_PORT` blank, and configure the intended database name and authentication in `.env`.

Services, packages, FAQs, testimonials, and journal posts are managed through Django Admin. A service, package, FAQ, or testimonial is public only after it is marked published. Testimonials also require confirmed consent before publication.

Enquiries and consultation requests are saved in SQL Server and can be reviewed in Django Admin. Consultation requests remain pending until an administrator confirms an appointment. Local development uses Django's console email backend; messages are printed in the server terminal. Configure SMTP and `BUSINESS_NOTIFICATION_EMAIL` through environment variables before enabling production email.

## Development phases

1. Public website, services, enquiries, bookings, and editable content.
2. Student accounts, applications, documents, and administration.
3. AI chatbot, payments, messaging, multilingual support, and analytics.
