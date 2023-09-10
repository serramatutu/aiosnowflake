"""A classical Snowflake Python connector application that generates various
requests to the Snowflake servers.

Run this in conjunction with `mitmproxy` to intercept its requests.
"""

import json
import os
from argparse import ArgumentParser, Namespace
from typing import Any

import snowflake.connector as sc
from dotenv import load_dotenv
from snowflake.connector.connection import SnowflakeConnection


def parse_arguments() -> Namespace:
    """Create an argument parser and parse args from stdin."""

    parser = ArgumentParser()
    parser.add_argument(
        "--queries",
        required=True,
        help="Comma-separated list of query file names from `tests/queries/`.",
    )
    return parser.parse_args()


def get_query_from_name(query_name: str) -> tuple[str, list[Any] | None]:
    """Return a query SQL and bound params given the filename in
    `tests/queries/`."""

    sql_full_path = os.path.abspath(f"../tests/queries/{query_name}.sql")
    with open(sql_full_path, "r") as file:
        sql_text = file.read()

    binds = None
    if query_name.endswith(".bind"):
        binds_full_path = os.path.abspath(f"../tests/queries/{query_name}.json")
        with open(binds_full_path, "r") as file:
            binds_text = file.read()
        binds = json.loads(binds_text)

    return sql_text, binds


def get_connection() -> SnowflakeConnection:
    """Create a SnowflakeConnection from environment variables."""

    organization = os.environ["SNOWFLAKE_ORGANIZATION"]
    account_name = os.environ["SNOWFLAKE_ACCOUNT"]
    account_identifier = f"{organization}-{account_name}"

    conn = sc.connect(
        user=os.environ["SNOWFLAKE_USERNAME"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=account_identifier,
        ocsp_fail_open=True,
        # use questionmarks for binds
        paramstyle="qmark",
    )

    return conn


def main():
    """The main function to the sample application.

    Run with `--help` to get usage instructions.
    """

    load_dotenv()

    args = parse_arguments()
    queries_comma_list = args.queries
    queries_list = queries_comma_list.split(",")

    conn = get_connection()

    print(f"Executing {len(queries_list)} queries...")

    for query_name in queries_list:
        sql, binds = get_query_from_name(query_name)
        print("Executing query:")
        print(sql)
        print("Binds: ")
        print(binds)

        resultset = conn.cursor().execute(command=sql, params=binds)
        df = resultset.fetch_pandas_all()
        print("Result DataFrame:")
        print(df)

        print("-------------------")

    print("Done")


if __name__ == "__main__":
    main()
