from abc import abstractmethod, ABC
from typing import Any

from starlette.requests import Request


class VoiceAssistantAbstractService(ABC):
    @abstractmethod
    async def handler(self, request_body: dict[str, Any]) -> tuple[dict[str, Any], str]:
        pass
