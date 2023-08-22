import json
import logging
import pickle
import typing
from pathlib import Path

from src import exceptions, models
from src.clients.dex import base as base_dex_provider

logger = logging.getLogger(__name__)


class LiquidityPoolExporter(object):
    def __init__(
        self, dex_provider_client: base_dex_provider.BaseDexLPProvider
    ) -> None:
        self._provider_client = dex_provider_client
        self.log_prefix = "[{}-{}-{}-LIQUIDITY-POOL-EXPORTER]".format(
            self._provider_client.chain.name,
            self._provider_client.dex.name,
            self._provider_client.liquidity_pool.name,
        )

    def get_liquidity_provider_data(self) -> typing.List[typing.Dict]:
        transaction_events = models.TransactionEvent.objects.filter(
            transaction__contract_address=self._provider_client.lp_contract_address
        ).select_related("transaction")

        return [
            {
                "contract_address": event.transaction.contract_address,
                "event_name": event.name,
                "topics": json.loads(event.topics),
                "data": event.data,
                "block_number": event.transaction.block_number,
                "transaction_hash": event.transaction.transaction_hash,
                "transaction_index": event.transaction.transaction_index,
                "block_hash": event.transaction.block_hash,
                "log_index": event.log_index,
                "transaction_from_address": event.transaction.from_address,
                "transaction_to_address": event.transaction.to_address,
                "transaction_gas": event.transaction.gas,
                "transaction_gas_price": event.transaction.gas_price,
            }
            for event in transaction_events
        ]

    def persist_pickle(
        self, data: typing.List[typing.Dict], path: str, overwrite_file: bool = False
    ) -> None:
        file_path = Path(path)
        if not file_path.parent.exists():
            msg = "Directory for pickle file does not exist (path={}).".format(
                path,
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.LiquidityPoolExporterException(msg)

        if file_path.exists() and not overwrite_file:
            msg = "Pickle file already exists, use --overwrite to override it (path={}).".format(
                path,
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise exceptions.LiquidityPoolExporterException(msg)

        with open("{}.pkl".format(file_path), "wb") as pickle_file:
            pickle.dump(data, pickle_file)

        logger.info("Saved data to pickle file: '{}'.".format(file_path))
