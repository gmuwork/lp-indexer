import typing
from dataclasses import dataclass


@dataclass
class TransactionEvent:
    name: str
    contract_address: str
    topics: typing.List[str]
    data: str
    transaction_hash: str
    log_index: int


@dataclass
class Transaction:
    block_number: int
    block_hash: str
    from_address: str
    to_address: typing.Optional[str]
    gas: int
    gas_price: int
    transaction_hash: str
    transaction_index: int
