**⚠️ aiosnowflake is far from being feature-complete and is not endorsed by Snowflake ⚠️**

# aiosnowflake

aiosnowflake is an attempt to implement a [long awaited](https://github.com/snowflakedb/snowflake-connector-python/issues/38) (no pun intended) [asyncio](https://docs.python.org/3/library/asyncio.html)-compatible [Snowflake](https://www.snowflake.com/en/) Python connector.

It uses [aiohttp](https://docs.aiohttp.org/en/stable/index.html) to connect to [Snowflake's SQL API](https://docs.snowflake.com/en/developer-guide/sql-api/index) to perform all underlying operations.

At its current state, its not ready for usage and there are a lot of things missing, including documentation.
