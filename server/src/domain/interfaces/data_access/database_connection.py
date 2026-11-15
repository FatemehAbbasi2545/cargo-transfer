from abc import ABC, abstractmethod

class IDatabaseConnection(ABC):    
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

   


