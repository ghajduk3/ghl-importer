import enum


class LoanDataPoolStatus(enum.Enum):
    UNPROCESSED = 1
    IN_PROCESS = 2
    PROCESSED = 3
    UNPROCESSABLE = 4
