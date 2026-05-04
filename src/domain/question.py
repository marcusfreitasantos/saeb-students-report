
from enum import Enum

class DifficultyLevel(Enum):
    EASY = "Fácil"
    MEDIUM = "Médio"
    HARD = "Difícil"

class Question:
    def __init__(self, descriptor:str, level: DifficultyLevel, description: str, options: list, answer: str):
        self.descriptor = descriptor
        self.level = level
        self.description = description
        self.options = options
        self.answer = answer

    @property
    def descriptor(self):
        return self._descriptor

    @descriptor.setter
    def descriptor(self, d):
        if not d: raise Exception("descriptor cannot be empty")
        self._descriptor = d

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, l):
        if not isinstance(l, DifficultyLevel):
            raise Exception("level must be an instance of DifficultyLevel")
        self._level = l

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, l):
        if not isinstance(l, DifficultyLevel):
            raise Exception("level must be an instance of DifficultyLevel")
        self._level = l

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, d):
        if not d: raise Exception("description cannot be empty")
        self._description = d

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, o):
        if not isinstance(o, list):
            raise Exception("options must be a list")
        self._options = o

    @property
    def answer(self):
        return self._answer
    
    @answer.setter
    def answer(self, a):
        if not a: raise Exception("answer cannot be empty")
        self._answer = a
