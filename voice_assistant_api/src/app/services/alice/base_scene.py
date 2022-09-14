import logging
from abc import ABC, abstractmethod
from typing import Optional, Any

from app.services.alice.request import AliceRequest
from app.services.alice.response_helpers import make_button
from app.services.alice.state import STATE_RESPONSE_KEY

logger = logging.getLogger(__name__)


class Scene(ABC):
    @classmethod
    def id(cls):
        return cls.__name__

    @abstractmethod
    async def reply(self, request):
        """Метод генерации ответа сцены"""
        pass

    def move(self, request: AliceRequest):
        """Метод проверки перехода к новой сцене"""
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self, request: AliceRequest):
        pass

    @abstractmethod
    def handle_local_intents(self, request: AliceRequest) -> Optional[str]:
        pass

    async def fallback(self, request: AliceRequest):
        """Метод обработки неопознанного намерения в запросе пользователя"""
        text = 'Извините, я вас не поняла. Пожалуйста, попробуйте переформулировать вопрос.'
        logger.error(f'Unidentified intent. Original_utterance: {request.original_utterance}')

        return await self.make_response(
            text, buttons=[make_button('Что ты умеешь?', hide=True)]
        )

    async def make_response(
        self,
        text: str,
        tts: Optional[str] = None,
        card: Optional[dict[str, Any]] = None,
        state: Optional[dict[str, Any]] = None,
        buttons: Optional[list[dict[str, Any]]] = None,
        directives: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Метод создания ответа webhook

        :param text: Текст, который следует показать и озвучить пользователю. Максимум 1024 символа.
            Не должен быть пустым.
        :param tts: Ответ в формате TTS (text-to-speech). Максимум 1024 символа.
        :param card: Описание карточки — сообщения с поддержкой изображений. Если приложению удается отобразить
            карточку для пользователя, свойство response.text не используется. Содержимое зависит от типа карточки,
            указанного в поле card.type. Возможные значения:
            BigImage — одно изображение.
            ItemsList — список из нескольких изображений (от 1 до 5).
            ImageGallery — галерея из нескольких изображений (от 1 до 7).
        :param state: Объект, содержащий состояние навыка для хранения в контексте сессии.
        :param buttons: Кнопки, которые следует показать пользователю. Все указанные кнопки выводятся после основного
            ответа Алисы, описанного в свойствах response.text и response.card. Кнопки можно использовать как релевантные
            ответу ссылки или подсказки для продолжения разговора.
        :param directives: Директивы. Содержимое зависит от типа директивы. Возможные значения:
            audio_player — запуск аудиоплеера на умных колонках;
            start_account_linking — запуск процесса авторизации в навыке;
            start_purchase — запуск сценария оплаты;
            confirm_purchase — подтверждение оплаты навыком.
        :return: Возвращает словарь параметров для ответа Алисе.
        """
        if not text:
            text = (
                'К сожалению, по вашему запросу ничего не нашлось. '
                'Попробуйте спросить что-нибудь еще!'
            )
        elif len(text) > 1024:
            text = text[:1024]
        if tts is None:
            text_tts = text.replace('\n', ' sil <[680]> ')
            tts = text_tts[:1024]

        response = {
            'text': text,
            'tts': tts,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives

        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {'scene': self.id(), 'last_phrase': text},
        }

        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
        return webhook_response
