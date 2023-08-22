import abc
import typing

import web3
from django.conf import settings

from src import enums
from src.clients.dex import messages as dex_messages


class BaseDexLPProvider(object):
    LP_CONFIG = settings.CHAIN_DEX_LP_CONFIG

    def __init__(
        self, chain: enums.Chain, dex: enums.Dex, liquidity_pool: enums.LiquidityPool
    ) -> None:
        self.chain = chain
        self.dex = dex
        self.liquidity_pool = liquidity_pool
        self._web3_client = None
        self.log_prefix = "[{}-{}-{}-PROVIDER]".format(
            self.chain.name, self.dex.name, self.liquidity_pool.name
        )

    @property
    def chain_config(self) -> typing.Dict:
        return self.LP_CONFIG[self.chain.name]

    @property
    def dex_config(self) -> typing.Dict:
        return self.chain_config["dexes"][self.dex.name]

    @property
    def liquidity_pool_config(self) -> typing.Dict:
        return self.dex_config["pools"][self.liquidity_pool.name]

    @property
    def lp_contract_address(self) -> str:
        return web3.Web3.to_checksum_address(
            value=self.liquidity_pool_config["contract_address"]
        )

    @property
    def chain_node_validator_url(self) -> str:
        return self.chain_config["validator_node_url"]

    @property
    def max_events_block_diff(self) -> int:
        return self.dex_config["max_events_block_diff"]

    def get_web3_client(self) -> web3.Web3:
        if not self._web3_client:
            self._web3_client = web3.Web3(
                web3.Web3.HTTPProvider(endpoint_uri=self.chain_node_validator_url)
            )

        return self._web3_client

    @abc.abstractmethod
    def get_transaction_events(
        self,
        from_block: typing.Union[str, int] = "earliest",
        to_block: typing.Union[str, int] = "latest",
    ) -> typing.List[dex_messages.TransactionEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_transaction(self, transaction_hash: str) -> dex_messages.Transaction:
        raise NotImplementedError

    def get_latest_block_number(self) -> int:
        return self.get_web3_client().eth.block_number
