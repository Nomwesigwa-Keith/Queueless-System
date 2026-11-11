# QueueLess Uganda

QueueLess is a multi-role queue-management application for small businesses.

## Architecture

- `frontend/`: React + Vite web application
- `backend/`: Django REST API with PostgreSQL
- `vercel.json`: Vercel frontend deployment and `/api` routing

The customer, staff, and platform-admin dashboards are separate routes. Authentication uses JWT tokens. Queue state is stored in PostgreSQL rather than browser storage. Customers search the approved business directory, select a business and service, then join that business's queue. Pending and suspended businesses are hidden from the directory.

## Local development

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Set `VITE_API_URL=http://127.0.0.1:8000/api` for local development.

After updating an existing checkout, run `python manage.py migrate` again to apply the business, staff, queue, notification, and subscription tables.

The demo seed creates `Amara Salon` and can be rerun safely with `python manage.py seed_demo`.

## Deployment

Set the Vercel project root to the repository root and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `DJANGO_SECRET_KEY`: a long random secret
- `DJANGO_ALLOWED_HOSTS`: deployed hostname
- `VITE_API_URL`: `/api` when using the Vercel API route

Never commit `.env` files or production credentials.
