from abc import ABC, abstractmethod
from typing import Any
from app.schemas.integration import IncomingMessage, OutgoingMessage

class MessagingPlatform(ABC):
    @abstractmethod
    async def receive_message(self, payload: dict[str, Any]) -> IncomingMessage | None:
        """Parses a webhook payload into an internal IncomingMessage format."""
        pass

    @abstractmethod
    async def send_message(self, message: OutgoingMessage) -> bool:
        """Sends an OutgoingMessage back to the platform."""
        pass

    @abstractmethod
    async def get_user(self, platform_user_id: str) -> dict[str, Any]:
        """Retrieves user information from the platform."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if the platform API is reachable."""
        pass
