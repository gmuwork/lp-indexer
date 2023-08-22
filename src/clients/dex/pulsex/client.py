import logging
import typing

from common import exceptions as common_exceptions
from common import utils as common_utils
from src import enums
from src.clients.dex import base as base_dex_provider
from src.clients.dex import exceptions as dex_exceptions
from src.clients.dex import messages as dex_messages
from src.clients.dex.pulsex import constants as pulsex_constants
from src.clients.dex.pulsex import schemas as pulsex_schemas

logger = logging.getLogger(__name__)


class PulseXDexProvider(base_dex_provider.BaseDexLPProvider):
    def __init__(self, chain: enums.Chain, dex: enums.Dex, liquidity_pool: enums.LiquidityPool) -> None:
        super().__init__(chain=chain, dex=dex, liquidity_pool=liquidity_pool)

    def get_transaction_events(
        self,
        from_block: typing.Union[str, int] = "earliest",
        to_block: typing.Union[str, int] = "latest",
    ) -> typing.List[dex_messages.TransactionEvent]:
        try:
            response = self.get_web3_client().eth.get_logs(
                {
                    "address": self.lp_contract_address,
                    "fromBlock": from_block,
                    "toBlock": to_block,
                }
            )
        except Exception as e:
            msg = "Unable to get contract events (contract_address={}, from_block={}, to_block={}). Error: {}".format(
                self.lp_contract_address,
                from_block,
                to_block,
                common_utils.get_exception_message(exception=e),
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise dex_exceptions.DexProviderClientException(msg)

        try:
            validated_response_data = common_utils.validate_data_schema(
                data=[dict(response_item) for response_item in response],
                schema=pulsex_schemas.TransactionEvents(),
            )
        except common_exceptions.ValidationSchemaException as e:
            msg = "Unable to validate events data (raw_data={}). Error: {}".format(
                response, common_utils.get_exception_message(exception=e)
            )
            logger.error("{} {}.".format(self.log_prefix, msg))
            raise dex_exceptions.DexProviderDataValidationError(msg)

        return [
            dex_messages.TransactionEvent(
                name=pulsex_constants.EVENT_SIGNATURES_NAME_MAP[event["topics"][0]],
                contract_address=event["contract_address"],
                topics=event["topics"],
                data=event["data"],
                transaction_hash=event["transaction_hash"],
                log_index=event["log_index"],
            )
            for event in validated_response_data["transaction_events"]
        ]

    def get_transaction(self, transaction_hash: str) -> dex_messages.Transaction:
        try:
            response = self.get_web3_client().eth.get_transaction(transaction_hash=transaction_hash)
        except Exception as e:
            msg = "Unable to get transaction (contract_address={}, transaction_hash={}). Error: {}".format(
                self.lp_contract_address,
                transaction_hash,
                common_utils.get_exception_message(exception=e),
            )
            logger.exception("{} {}.".format(self.log_prefix, msg))
            raise dex_exceptions.DexProviderClientException(msg)

        try:
            validated_response_data = common_utils.validate_data_schema(
                data=dict(response),
                schema=pulsex_schemas.Transaction(),
            )
        except common_exceptions.ValidationSchemaException as e:
            msg = "Unable to validate transaction data (raw_data={}). Error: {}".format(
                response, common_utils.get_exception_message(exception=e)
            )
            logger.error("{} {}.".format(self.log_prefix, msg))
            raise dex_exceptions.DexProviderDataValidationError(msg)

        return dex_messages.Transaction(
            transaction_hash=validated_response_data["transaction_hash"],
            transaction_index=validated_response_data["transaction_index"],
            block_number=validated_response_data["block_number"],
            block_hash=validated_response_data["block_hash"],
            from_address=validated_response_data["from_address"],
            to_address=validated_response_data["to_address"],
            gas=validated_response_data["gas"],
            gas_price=validated_response_data["gas_price"],
        )
