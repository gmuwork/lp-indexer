import logging
import typing

from django.conf import settings

from src import enums
from src.clients.dex import exceptions as provider_exceptions
from src.clients.dex.pulsex import client as pulsex_client

logger = logging.getLogger(__name__)


class DexProviderFactory(object):
    _LOG_PREFIX = "[DEX-PROVIDER-FACTORY]"
    _PROVIDER_IMPLEMENTATION_MAP = {
        enums.Dex.PULSEX: pulsex_client.PulseXDexProvider,
    }

    @classmethod
    def create(
        cls,
        chain: enums.Chain,
        dex: enums.Dex,
        liquidity_pool: enums.LiquidityPool,
    ) -> pulsex_client.PulseXDexProvider:
        if not settings.CHAIN_DEX_LP_CONFIG[chain.name]["dexes"][dex.name]["pools"][liquidity_pool.name][
            "is_active"
        ]:
            msg = "Liquidity pool {} is not active on dex {} for chain {}".format(
                liquidity_pool.name, dex.name, chain.name
            )
            logger.error("{} {}.".format(cls._LOG_PREFIX, msg))
            raise provider_exceptions.DexProviderException(msg)

        if dex not in cls._PROVIDER_IMPLEMENTATION_MAP:
            msg = "Dex {} is not supported".format(dex.name)
            logger.error("{} {}.".format(cls._LOG_PREFIX, msg))
            raise provider_exceptions.DexProviderException(msg)

        return cls._PROVIDER_IMPLEMENTATION_MAP[dex](chain=chain, dex=dex, liquidity_pool=liquidity_pool)
