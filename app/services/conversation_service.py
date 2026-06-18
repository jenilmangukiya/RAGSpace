from uuid import UUID
from app.models import Message
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from app.models.conversation import Conversation


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(
        self,
        app_id: str,
        user_id: str,
    ):
        conversation = Conversation(app_id=app_id, user_id=user_id, title="New chat")

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def list_conversations(self, app_id: str, user_id: str):
        conversations = (
            self.db.query(Conversation)
            .filter(Conversation.app_id == app_id, Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .all()
        )

        return conversations

    def get_conversation(self, conversation_id: str, user_id: str):
        conversation = (
            self.db.query(Conversation)
            .options(joinedload(Conversation.messages))
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )
        if conversation:
            conversation.messages.sort(key=lambda m: m.created_at)
        return conversation

    def get_conversation_latest_history(self, conversation_id: str, user_id: str):
        messages = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
            )
            .order_by(Message.created_at.desc())
            .limit(20)
            .all()
        )
        return messages[::-1]

    def create_message(
        self,
        user_id: str,
        app_id: str,
        conversation_id: str,
        role: str,
        content: str,
    ):
        message = Message(
            user_id=user_id,
            app_id=app_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def create_messages(self, messages: list[Message]):
        self.db.add_all(messages)
        self.db.commit()

    def save_chat_exchange(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
    ):
        # Update conversation title if it is default ("New chat" or "New Chat")
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        if conversation and conversation.title in ("New chat", "New Chat"):
            title = user_message.strip()
            if len(title) > 40:
                title = title[:40] + "..."
            conversation.title = title

        messages = [
            Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
            ),
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_message,
            ),
        ]
        print(messages)
        self.db.add_all(messages)
        self.db.commit()

    def delete_conversation(self, conversation_id: str, user_id: str):
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return {"message": "Conversation deleted successfully"}
        return {"message": "Conversation not found"}

    def rename_conversation(self, conversation_id: str, title: str, user_id: str):
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )
        if conversation:
            conversation.title = title
            self.db.commit()
            self.db.refresh(conversation)
            return conversation
        return None
