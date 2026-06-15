from uuid import UUID
from sqlalchemy.orm import Session

from app.models.app import App


class AppService:
    def __init__(self, db: Session):
        self.db = db

    # Create new App
    async def create_app(self, name: str, user_id: UUID) -> App:
        app = App(name=name, user_id=user_id)

        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)

        return app

    async def get_apps(self, user_id: UUID) -> list[App]:
        apps = (
            self.db.query(App)
            .filter(App.user_id == user_id)
            .order_by(App.created_at.desc())
            .all()
        )

        return apps

    async def delete_app(self, app_id: UUID, user_id: UUID):
        app = (
            self.db.query(App).filter(App.id == app_id, App.user_id == user_id).first()
        )

        if not app:
            return False

        self.db.delete(app)
        self.db.commit()

        return True
