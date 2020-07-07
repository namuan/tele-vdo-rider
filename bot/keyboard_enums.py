from enum import Enum, auto


# Enum for keyboard buttons
class KeyboardEnum(Enum):
    BUY = auto()
    SELL = auto()
    YES = auto()
    NO = auto()
    CANCEL = auto()

    def clean(self):
        return self.name.replace("_", " ")
