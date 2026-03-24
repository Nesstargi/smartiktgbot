from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models.bot_subscriber import BotSubscriber
from backend.models.lead import Lead
from backend.schemas.bot_subscriber import BotSubscriberRegisterIn


class BotSubscriberService:
    @staticmethod
    def register(db: Session, data: BotSubscriberRegisterIn) -> BotSubscriber:
        chat_id = str(data.chat_id).strip()
        subscriber = (
            db.query(BotSubscriber)
            .filter(BotSubscriber.chat_id == chat_id)
            .first()
        )
        now = datetime.now(timezone.utc)

        payload = {
            "telegram_user_id": str(data.telegram_user_id).strip() if data.telegram_user_id is not None else None,
            "username": data.username,
            "full_name": data.full_name,
            "last_seen_at": now,
        }

        if subscriber is None:
            subscriber = BotSubscriber(
                chat_id=chat_id,
                created_at=now,
                **payload,
            )
            db.add(subscriber)
        else:
            for key, value in payload.items():
                setattr(subscriber, key, value)

        db.commit()
        db.refresh(subscriber)
        return subscriber

    @staticmethod
    def broadcast_chat_ids(db: Session) -> list[str]:
        unique_chat_ids: list[str] = []
        seen: set[str] = set()

        def append(value):
            if value is None:
                return
            chat_id = str(value).strip()
            if not chat_id or chat_id in seen:
                return
            seen.add(chat_id)
            unique_chat_ids.append(chat_id)

        subscriber_rows = db.query(BotSubscriber.chat_id).all()
        lead_rows = (
            db.query(Lead.telegram_id)
            .filter(Lead.telegram_id.isnot(None))
            .all()
        )

        for row in subscriber_rows:
            append(row[0])
        for row in lead_rows:
            append(row[0])

        return unique_chat_ids
