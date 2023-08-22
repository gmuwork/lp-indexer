class DexProviderException(Exception):
    pass


class DexProviderClientException(DexProviderException):
    pass


class DexProviderDataValidationError(DexProviderException):
    pass
