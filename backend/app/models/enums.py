import enum

class CreatureType(str, enum.Enum):
    PLAYER = "player"
    ENEMY = "enemy"
    ALLY = "ally"
    OTHER = "other"