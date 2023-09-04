from django.db import models as django_db_models


class Transaction(django_db_models.Model):
    transaction_hash = django_db_models.CharField(null=False, max_length=255)
    transaction_index = django_db_models.IntegerField(null=False)
    contract_address = django_db_models.CharField(null=False, max_length=255)
    block_number = django_db_models.IntegerField(null=False)
    block_hash = django_db_models.CharField(null=False, max_length=255)
    from_address = django_db_models.CharField(null=False, max_length=255)
    to_address = django_db_models.CharField(null=True, max_length=255)
    gas = django_db_models.CharField(null=False, max_length=255)
    gas_price = django_db_models.CharField(null=False, max_length=255)

    created_at = django_db_models.DateTimeField(auto_now_add=True)
    updated_at = django_db_models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "src"
        db_table = "lp_pool_transaction"
        indexes = [
            django_db_models.Index(fields=["transaction_hash"]),
            django_db_models.Index(fields=["contract_address"]),
        ]


class TransactionEvent(django_db_models.Model):
    name = django_db_models.CharField(null=False, max_length=255)
    topics = django_db_models.TextField(null=False)
    data = django_db_models.TextField(null=False)
    log_index = django_db_models.IntegerField(null=False)

    created_at = django_db_models.DateTimeField(auto_now_add=True)
    updated_at = django_db_models.DateTimeField(auto_now=True)

    transaction = django_db_models.ForeignKey(
        Transaction, on_delete=django_db_models.CASCADE
    )

    class Meta:
        app_label = "src"
        db_table = "lp_pool_transaction_event"
        indexes = [django_db_models.Index(fields=["log_index", "transaction_id"])]


class LiquidityPoolImporterBlockReference(django_db_models.Model):
    chain = django_db_models.IntegerField(null=False)
    chain_name = django_db_models.CharField(null=False, max_length=255)
    dex = django_db_models.IntegerField(null=False)
    dex_name = django_db_models.CharField(null=False, max_length=255)
    liquidity_pool = django_db_models.IntegerField(null=False)
    liquidity_pool_name = django_db_models.CharField(null=False, max_length=255)
    block_number = django_db_models.IntegerField(null=False)
    block_hash = django_db_models.CharField(null=False, max_length=255)

    created_at = django_db_models.DateTimeField(auto_now_add=True)
    updated_at = django_db_models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "src"
        db_table = "lp_pool_block_reference"
