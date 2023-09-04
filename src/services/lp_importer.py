import json
import logging

from django.db import transaction

from common import utils as common_utils
from src import exceptions, models
from src.clients.dex import base as base_dex_provider
from src.clients.dex import exceptions as dex_exceptions

logger = logging.getLogger(__name__)


class LiquidityPoolImporter(object):
    def __init__(
        self, dex_provider_client: base_dex_provider.BaseDexLPProvider
    ) -> None:
        self._provider_client = dex_provider_client
        self.log_prefix = "[{}-{}-{}-LIQUIDITY-POOL-IMPORTER]".format(
            self._provider_client.chain.name,
            self._provider_client.dex.name,
            self._provider_client.liquidity_pool.name,
        )

    def import_liquidity_provider_data(self) -> None:
        block_reference = models.LiquidityPoolImporterBlockReference.objects.filter(
            chain=self._provider_client.chain.value,
            dex=self._provider_client.dex.value,
            liquidity_pool=self._provider_client.liquidity_pool.value,
        ).first()

        if not block_reference:
            logger.info(
                "{} No block reference found. Please create initial block reference.".format(
                    self.log_prefix
                )
            )
            return

        from_block_number = block_reference.block_number
        to_block_number = self._provider_client.get_latest_block_number()
        logger.info(
            "{} Importing all liquidity provider data (from_block={}, to_block={}, block_diff={}).".format(
                self.log_prefix,
                from_block_number,
                to_block_number,
                to_block_number - from_block_number,
            )
        )

        while True:
            try:
                self._import_liquidity_provider_batch_data(
                    from_block=from_block_number,
                    to_block=from_block_number
                    + self._provider_client.max_events_block_diff,
                )
            except dex_exceptions.DexProviderException as e:
                msg = "Unable to import liquidity provider data for block range (from_block={}, to_block={}). Error: {}".format(
                    from_block_number,
                    from_block_number + self._provider_client.max_events_block_diff,
                    common_utils.get_exception_message(exception=e),
                )
                logger.exception("{} {}.".format(self.log_prefix, msg))
                raise exceptions.LiquidityPoolImporterException(msg)

            from_block_number += self._provider_client.max_events_block_diff
            if from_block_number > to_block_number:
                break

        block_reference.block_number = to_block_number
        block_reference.save(update_fields=["block_number", "updated_at"])

        logger.info(
            "{} Imported all liquidity provider data (from_block={}, to_block={}). Set block reference (id={}) to current block number '{}'.".format(
                self.log_prefix,
                from_block_number,
                to_block_number,
                block_reference.id,
                to_block_number,
            )
        )

    def _import_liquidity_provider_batch_data(
        self, from_block: int, to_block: int
    ) -> None:
        logger.info(
            "{} Batch importing liquidity provider data (from_block={}, to_block={}).".format(
                self.log_prefix, from_block, to_block
            )
        )
        transaction_events = self._provider_client.get_transaction_events(
            from_block=from_block,
            to_block=to_block,
        )
        logger.info(
            "{} Fetched {} transaction events to import.".format(
                self.log_prefix, len(transaction_events)
            )
        )
        for transaction_event in transaction_events:
            with transaction.atomic():
                tx = models.Transaction.objects.filter(
                    transaction_hash=transaction_event.transaction_hash
                ).first()
                if not tx:
                    transaction_data = self._provider_client.get_transaction(
                        transaction_hash=transaction_event.transaction_hash
                    )
                    tx = models.Transaction.objects.create(
                        transaction_hash=transaction_data.transaction_hash,
                        transaction_index=transaction_data.transaction_index,
                        contract_address=transaction_event.contract_address,
                        block_number=transaction_data.block_number,
                        block_hash=transaction_data.block_hash,
                        from_address=transaction_data.from_address,
                        to_address=transaction_data.to_address,
                        gas=transaction_data.gas,
                        gas_price=transaction_data.gas_price,
                    )
                    logger.info(
                        "{} Imported new transaction (id={}, transaction_hash={}).".format(
                            self.log_prefix, tx.id, tx.transaction_hash
                        )
                    )

                event = models.TransactionEvent.objects.filter(
                    transaction_id=tx.id,
                    log_index=transaction_event.log_index,
                ).first()
                if not event:
                    event = models.TransactionEvent.objects.create(
                        name=transaction_event.name,
                        topics=json.dumps(transaction_event.topics),
                        data=transaction_event.data,
                        log_index=transaction_event.log_index,
                        transaction=tx,
                    )

                logger.info(
                    "{} Imported new event (event_id={}, transaction_id={}).".format(
                        self.log_prefix, event.id, tx.id
                    )
                )
        logger.info(
            "{} Batch imported liquidity provider data (from_block={}, to_block={}).".format(
                self.log_prefix, from_block, to_block
            )
        )
