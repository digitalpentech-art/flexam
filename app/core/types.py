from enum import Enum

class FieldType(Enum):
    STRING = 'string'
    INTEGER = 'integer'
    DECIMAL = 'decimal'
    BOOLEAN = 'boolean'
    DATE = 'date'
    DATETIME = 'datetime'
    UUID = 'uuid'
    JSON = 'json'
    REFERENCE = 'reference'

    @classmethod
    def list(cls):
        return [c.value for c in cls]
