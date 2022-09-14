import abc
import json
import logging
import os
import reprlib
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""
        pass


class JsonFileStorage(BaseStorage):
    """Class for save state to persistent storage in JSON format"""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        if self.file_path is None:
            self.file_path = os.path.join(os.path.dirname(__file__), 'state.json')
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            self.save_state({})

    def save_state(self, state: dict) -> None:
        with open(self.file_path, 'w') as write_file:
            json.dump(state, write_file)
            logger.debug('Save state: %s to file %s', reprlib.repr(state), self.file_path)

    def retrieve_state(self) -> dict:
        if not os.path.exists(self.file_path):
            logger.info('File %s not exists. Will be return empty dictionary', self.file_path)
            return dict()
        if os.path.getsize(self.file_path) == 0:
            logger.info('File %s is empty. Will be return empty dictionary', self.file_path)
            return dict()
        with open(self.file_path, 'r') as read_file:
            try:
                state = json.load(read_file)
                if state is not None and isinstance(state, dict):
                    logger.debug(
                        'Read state: %s from the file %s', reprlib.repr(state), self.file_path
                    )
                    return state
                else:
                    return dict()
            except json.JSONDecodeError:
                logger.error('File %s does not contain data in JSON format', self.file_path)
                return dict()


class State:
    """
    Class for storing the state when working with data, so as not to constantly re-read the data from the beginning.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key"""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Get the state by a specific key"""
        state = self.storage.retrieve_state()
        value = state.get(key, None)
        return value
