import enum


class LoanDataPoolStatus(enum.Enum):
    UNPROCESSED = 1
    PROCESSED = 3
    UNPROCESSABLE = 4


class ContactAction(enum.Enum):
    CREATED = 1
    UPDATED = 2


class ContactCustomField(enum.Enum):
    LEAD_STAGE = "oRL38kB70sg8xaNU9ago"
    SUBJECT_PROPERTY_ADDRESS = "Dc4EcZVN7AI1p4vd8o9A"
    SUBJECT_PROPERTY_ZIP_CODE = "QDnihCKlMr6Q5nKBYdUl"
    SUBJECT_PROPERTY_CITY = "MSGxEVEj8MsnWfzqwxYz"
    SUBJECT_PROPERTY_STATE = "qmcFjFB9I9gg0SHdqsbq"
    CONTACT_ID = "2jziBvouSz3gwUkk3qPA"
    LOAN_OFFICER_NAME = "ol7hG5L4nZ0OJyWJMTd3"
    LOAN_OFFICER_EMAIL = "KvaiYH3jlksGhGgZ4YSh"
    LOAN_STATUS = "xh5uzMmrck5qU5PBoy4Z"
    LOAN_ID = "Tsc0czPAGOwD224K17u0"
