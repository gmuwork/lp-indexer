import typing

import marshmallow


class Schema(marshmallow.schema.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


class TransactionEvent(Schema):
    contract_address = marshmallow.fields.Str(required=True, data_key="address")
    topics = marshmallow.fields.List(marshmallow.fields.Str(), required=True, data_key="topics")
    data = marshmallow.fields.Str(required=True, data_key="data")
    transaction_hash = marshmallow.fields.Str(required=True, data_key="transactionHash")
    log_index = marshmallow.fields.Int(required=True, data_key="logIndex")

    @marshmallow.pre_load
    def pre_process_data(self, data: typing.Dict, **kwargs: typing.Any) -> typing.Dict:
        data["topics"] = [topic.hex() for topic in data["topics"]] if data.get("topics") else None
        data["data"] = data['data'].hex() if data.get("data") else None
        data["transactionHash"] = data["transactionHash"].hex() if data.get("transactionHash") else None

        return data


class TransactionEvents(Schema):
    transaction_events = marshmallow.fields.Nested(TransactionEvent, many=True)

    @marshmallow.pre_load
    def pre_process_data(self, data: typing.List[typing.Dict], **kwargs: typing.Any) -> typing.Dict:
        return {"transaction_events": data}


class Transaction(Schema):
    transaction_index = marshmallow.fields.Int(required=True, data_key="transactionIndex")
    transaction_hash = marshmallow.fields.Str(required=True, data_key="hash")
    block_number = marshmallow.fields.Int(required=True, data_key="blockNumber")
    block_hash = marshmallow.fields.Str(required=True, data_key="blockHash")
    from_address = marshmallow.fields.Str(required=True, data_key="from")
    to_address = marshmallow.fields.Str(required=False, data_key="to", missing=None)
    gas = marshmallow.fields.Int(required=True, data_key="gas")
    gas_price = marshmallow.fields.Int(required=True, data_key="gasPrice")

    @marshmallow.pre_load
    def pre_process_data(self, data: typing.Dict, **kwargs: typing.Any) -> typing.Dict:
        data["hash"] = data["hash"].hex() if data.get("hash") else None

        data["blockHash"] = data["blockHash"].hex() if data.get("blockHash") else None

        return data
