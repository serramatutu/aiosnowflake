"""A classical Snowflake Python connector application that generates various
requests to the Snowflake servers.

Run this in conjunction with `mitmproxy` to intercept its requests.
"""

import os
from argparse import ArgumentParser, Namespace

import snowflake.connector as sc
from dotenv import load_dotenv
from snowflake.connector.connection import SnowflakeConnection


def parse_arguments() -> Namespace:
    """Create an argument parser and parse args from stdin."""

    parser = ArgumentParser()
    parser.add_argument("--query", required=True)
    return parser.parse_args()


def get_query_from_name(query_name: str) -> str:
    """Return a query SQL given the filename in `tests/queries/`."""

    full_path = os.path.abspath(f"../tests/queries/{query_name}.sql")
    with open(full_path, "r") as file:
        sql_text = file.read()
    return sql_text


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
    )

    return conn


def main():
    """The main function to the sample application.

    Run with `--help` to get usage instructions.
    """

    load_dotenv()

    args = parse_arguments()
    query_name = args.query

    query_text = get_query_from_name(query_name)
    print("Executing query:")
    print(query_text)

    conn = get_connection()

    resultset = conn.cursor().execute(query_text)
    df = resultset.fetch_pandas_all()
    print("Result DataFrame:")
    print(df)

    print("Done")


if __name__ == "__main__":
    main()
