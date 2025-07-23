import re

from ofx_converter.parsing.ofx_transaction_parser import OfxTransactionParser


class NubankTransactionParser(OfxTransactionParser):

    def _is_installment(self, memo: str) -> bool:
        is_installment = super()._is_installment(memo)
        discount_match = re.search("Desconto Antecipação", memo)
        is_discount = discount_match is not None
        return is_installment or is_discount
