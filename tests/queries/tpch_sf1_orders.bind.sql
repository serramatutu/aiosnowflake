SELECT O_ORDERKEY, O_ORDERDATE, O_TOTALPRICE
FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
WHERE O_ORDERSTATUS = ?
ORDER BY O_ORDERKEY
LIMIT 500
