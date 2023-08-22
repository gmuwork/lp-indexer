import typing

from django.conf import settings

from src import enums


def get_liquidity_pools(
    chain: enums.Chain, dex: enums.Dex
) -> typing.List[enums.LiquidityPool]:
    return [
        enums.LiquidityPool[liquidity_pool]
        for liquidity_pool in settings.CHAIN_DEX_LP_CONFIG[chain.name]["dexes"][
            dex.name
        ]["pools"].keys()
    ]
