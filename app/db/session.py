from app.db.postgres import SessionLocal


def create_db_session():
    return SessionLocal()
