import logging
import typing

from django.core.management.base import BaseCommand, CommandParser

from common import utils as common_utils
from src import enums, exceptions
from src.clients.dex import exceptions as dex_exceptions
from src.clients.dex import factory
from src.services import lp_exporter as lp_exporter_services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Queries offline data for a chosen liquidity pool on a given DEX and chain and persists it to a .pickle file.
            Offline data consists of events and transactions.
            ex. python manage.py query_pickle --chain=PULSE --dex=PULSEX --pool=WPLS_DAI --output-file=my_file.pkl  [--overwrite]
            """

    log_prefix = "[IMPORT-CONTINOUS-LIQUIDITY-PROVIDER-DATA]"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--chain",
            required=True,
            type=str,
            choices=[chain.name for chain in enums.Chain],
            help="Denotes the chain on which dex of liquidity pools is hosted.",
        )

        parser.add_argument(
            "--dex",
            required=True,
            type=str,
            choices=[dex.name for dex in enums.Dex],
            help="Denotes the DEX on which liquidity pools are hosted.",
        )

        parser.add_argument(
            "--pool",
            required=True,
            type=str,
            choices=[pool.name for pool in enums.LiquidityPool],
            help="Denotes the liquidity pool to be extracted.",
        )

        parser.add_argument(
            "--output-file",
            required=True,
            type=str,
            help="Path to the output pickle file.",
        )

        parser.add_argument(
            "--overwrite",
            required=False,
            type=bool,
            default=False,
            help="If the target pickle file already exists it will overwrite it.",
        )

    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        chain = enums.Chain[kwargs["chain"]]
        dex = enums.Dex[kwargs["dex"]]
        liquidity_pool = enums.LiquidityPool[kwargs["pool"]]
        output_path = kwargs["output_file"]
        overwrite_file = kwargs["overwrite"]

        logger.info(
            "{} Started command '{}' (chain={}, dex={}, liquidity_pool={}, output_path={}, overwrite_file={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                chain.name,
                dex.name,
                liquidity_pool.name,
                output_path,
                overwrite_file,
            )
        )

        try:
            lp_client = factory.DexProviderFactory().create(
                chain=chain, dex=dex, liquidity_pool=liquidity_pool
            )
        except dex_exceptions.DexProviderClientException as e:
            logger.exception(
                "{} Unable to create dex provider factory (chain={}, dex={}, liquidity_pool={}, output_path={}, overwrite_file={}). Error: {}.".format(
                    self.log_prefix,
                    chain.name,
                    dex.name,
                    liquidity_pool.name,
                    output_path,
                    overwrite_file,
                    common_utils.get_exception_message(exception=e),
                )
            )
            raise e

        try:
            exporter = lp_exporter_services.LiquidityPoolExporter(
                dex_provider_client=lp_client
            )
            transaction_data = exporter.get_liquidity_provider_data()
            exporter.persist_pickle(
                data=transaction_data,
                path=output_path,
                overwrite_file=overwrite_file,
            )
        except exceptions.LiquidityPoolImporterException as e:
            logger.exception(
                "{} {}.".format(
                    self.log_prefix, common_utils.get_exception_message(exception=e)
                )
            )
            raise e

        logger.info(
            "{} Finished command '{}' (chain={}, dex={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                chain.name,
                dex.name,
            )
        )
