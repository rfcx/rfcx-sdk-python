from abc import ABC, abstractmethod

DETECTIONS = 1

class ClassifierBase(ABC):
    @abstractmethod
    def score(self, filename):
        pass

    @property
    @abstractmethod
    def score_output(self):
        pass

    @property
    @abstractmethod
    def class_names(self):
        pass

    @property
    @abstractmethod
    def sample_rate(self):
        pass

    @property
    @abstractmethod
    def window_duration(self):
        pass

    @property
    @abstractmethod
    def window_step(self):
        pass

    @property
    @abstractmethod
    def codec(self):
        pass
