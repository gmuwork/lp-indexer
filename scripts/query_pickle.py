import argparse
import json
import logging
import pickle
import sqlite3
import typing
from pathlib import Path

liquidity_pool_contract_addresses = {
    "WPLS_DAI": "0xE56043671df55dE5CDf8459710433C10324DE0aE",  # This is case-sensitive
    # TODO: Will add others here
}

logger = logging.getLogger(__name__)
log_prefix = "[QT2P]"


def get_parsed_args():
    parser = argparse.ArgumentParser(
        prog="QT2P - Query Transaction to Pickle",
        description="Query stored transactional data - transactions & events to a pickle file.\nYou can filter by a given liquidity pool.",
    )
    parser.add_argument(
        "--pool",
        required=True,
        type=str,
        help="Denotes the liquidity pool to be extracted.",
    )
    parser.add_argument(
        "--sqlite-path",
        required=True,
        type=str,
        help="Path to the SQLite database file.",
    )
    parser.add_argument(
        "--output-file", required=True, type=str, help="Path to the output pickle file."
    )
    parser.add_argument(
        "--overwrite",
        required=False,
        action="store_true",
        help="If the target pickle file already exists it will overwrite it.",
    )
    return parser.parse_args()


def dict_factory(cursor, row):
    """
    Helps transform a SQLite row to a dictionary
    """
    fields = [column[0] for column in cursor.description]
    # return {key: (value if key != 'topics' else json.loads(value.replace("'", "\""))) for key, value in zip(fields, row)}
    return {
        key: (value if key != "topics" else json.loads(value))
        for key, value in zip(fields, row)
    }


def query_data(liquidity_pool, db_path: str) -> typing.List[typing.Dict]:
    sqlite_path = Path(db_path)
    if not sqlite_path.exists():
        msg = "SQLite file does not exist. (path={})".format(
            db_path,
        )
        logger.exception("{} {}.".format(log_prefix, msg))
        raise Exception(msg)

    if liquidity_pool not in liquidity_pool_contract_addresses:
        msg = "Liquidity pool not supported yet. (liquidity_pool={})".format(
            liquidity_pool,
        )
        logger.exception("{} {}.".format(log_prefix, msg))
        raise Exception(msg)

    contract_address = liquidity_pool_contract_addresses[liquidity_pool]
    query = """
        SELECT 
            contract_address,
            name,
            topics,
            data,
            block_number,
            transaction_hash,
            transaction_index,
            block_hash,
            log_index,
            from_address AS transaction_from_address,
            to_address AS transaction_to_address,
            gas AS transaction_gas,
            gas_price AS transaction_gas_price
        FROM lp_pool_transaction txs LEFT JOIN lp_pool_transaction_event events ON txs.id = events.transaction_id
        WHERE
            txs.contract_address = '{}'
    """.format(
        contract_address
    )
    db = sqlite3.connect(sqlite_path)
    db.row_factory = dict_factory
    results = db.execute(query).fetchall()

    return results


def persist_pickle(
    data: typing.List[typing.Dict], path: str, overwrite_file: bool = False
) -> None:
    file_path = Path(path)
    if not file_path.parent.exists():
        msg = "Directory for pickle file does not exist (path={}).".format(
            path,
        )
        logger.error("{} {}.".format(log_prefix, msg))
        raise Exception(msg)

    if file_path.exists() and not overwrite_file:
        msg = "Pickle file already exists (path={}).".format(
            path,
        )
        logger.error("{} {}.".format(log_prefix, msg))
        raise Exception(msg)

    with open("{}.pkl".format(file_path), "wb") as pickle_file:
        pickle.dump(data, pickle_file)

    logger.info("Saved data to pickle file {}".format(file_path))


def main():
    args = get_parsed_args()
    liquidity_pool = args.pool
    sqlite_path = args.sqlite_path
    path = args.output_file
    overwrite = args.overwrite
    logger.info("{} Exporting data to file='{}'.".format(log_prefix, path))

    try:
        transaction_data = query_data(
            liquidity_pool=liquidity_pool, db_path=sqlite_path
        )
        persist_pickle(data=transaction_data, path=path, overwrite_file=overwrite)
    except Exception as e:
        logger.exception(e)

    logger.info("{} Done.".format(log_prefix))


if __name__ == "__main__":
    main()
