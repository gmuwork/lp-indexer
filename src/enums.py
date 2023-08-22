import enum


class Chain(enum.Enum):
    PULSE = 1
    ETH = 2


class Dex(enum.Enum):
    PULSEX = 1
    UNISWAP = 2


class LiquidityPool(enum.Enum):
    WPLS_DAI = 1
    USDC_WPLS = 2
    WPLS_USDT = 3
    WBTC_WPLS = 4
    WETH_WPLS = 5
    WPLS_stETH = 6
    PLSX_WPLS = 7
    HEX_WPLS = 8
