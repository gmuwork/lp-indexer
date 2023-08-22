import logging
import typing

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from common import utils as common_utils
from src import enums, exceptions
from src.clients.dex import utils as dex_utils
from src.clients.dex import exceptions as dex_exceptions
from src.clients.dex import factory
from src.services import lp_importer as lp_importer_services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Maintains active authentication token pool.
            ex. python manage.py import_continous_liquidity_provider_data  --chain=PULSE --dex=PULSEX
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

    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        chain = enums.Chain[kwargs["chain"]]
        dex = enums.Dex[kwargs["dex"]]

        logger.info(
            "{} Started command '{}' (chain={}, dex={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                chain.name,
                dex.name,
            )
        )

        liquidity_pools = dex_utils.get_liquidity_pools(chain=chain, dex=dex)
        logger.info(
            "{} Found {} liquidity pools for which to import data (liquidity_pools={}).".format(
                self.log_prefix, len(liquidity_pools), liquidity_pools
            )
        )

        for liquidity_pool in liquidity_pools:
            try:
                lp_client = factory.DexProviderFactory().create(
                    chain=chain, dex=dex, liquidity_pool=liquidity_pool
                )
            except dex_exceptions.DexProviderClientException as e:
                logger.exception(
                    "{} Unable to create dex provider factory (chain={}, dex={}, liquidity_pool={}). Error: {}. Continue.".format(
                        self.log_prefix,
                        chain.name,
                        dex.name,
                        liquidity_pool.name,
                        common_utils.get_exception_message(exception=e),
                    )
                )
                continue

            try:
                lp_importer_services.LiquidityPoolImporter(
                    dex_provider_client=lp_client
                ).import_liquidity_provider_data()
            except exceptions.LiquidityPoolImporterException as e:
                logger.exception(
                    "{} {}. Continue.".format(
                        self.log_prefix, common_utils.get_exception_message(exception=e)
                    )
                )

        logger.info(
            "{} Finished command '{}' (chain={}, dex={}).".format(
                self.log_prefix,
                __name__.split(".")[-1],
                chain.name,
                dex.name,
            )
        )
