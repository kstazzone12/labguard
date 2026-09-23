# Database migrations

Alembic is configured for the SQLAlchemy model in `backend/app/models/entities.py`.

```bash
alembic upgrade head
```

The initial revision creates the complete abstract model. It contains no clinical reference limits; those values must arrive from explicit local configuration.
