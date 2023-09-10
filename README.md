**⚠️ aiosnowflake is far from being feature-complete and is not endorsed by Snowflake ⚠️**

# aiosnowflake

aiosnowflake is an attempt to implement a [long awaited](https://github.com/snowflakedb/snowflake-connector-python/issues/38) (no pun intended) [asyncio](https://docs.python.org/3/library/asyncio.html)-compatible [Snowflake](https://www.snowflake.com/en/) Python connector.

It uses [aiohttp](https://docs.aiohttp.org/en/stable/index.html) to connect to an **internal, undocumented API**. This is due to [Snowflake's SQL API](https://docs.snowflake.com/en/developer-guide/sql-api/index) not supporting adequate authorization schemes for a feature-complete SQL driver.

At its current state, its not ready for usage and there are a lot of things missing, including documentation.


## Developing

### API sniffing

As mentioned, aiosnowflake works on top of Snowflake's internal undocumented API. Exploring how it works is done by intercepting (sniffing) their original driver's requests to their servers, and reading its [source code](https://github.com/snowflakedb/snowflake-connector-python).

Learn more about how to sniff the driver [here](./sniff/README.md).
