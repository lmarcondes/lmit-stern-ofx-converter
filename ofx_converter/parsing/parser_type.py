from enum import Enum


class ParserType(Enum):
    XP_CSV = "xp-csv"
    XP_CARD_CSV = "xp-card-csv"
    NUBANK_OFX = "nubank-ofx"
    ITAU_CARD_XLSX = "itau-card-xlsx"
    OFX = "ofx"
