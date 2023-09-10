"""This whole module implements a sniffing tool for  intercepting HTTPS
requests from canonical the Snowflake Python connector to the Snowflake APIs.

This is helpful since the Snowflake connector uses undocumented APIs,
and simply using the SQL API limits the capabilities of aiosnowflake.
"""
