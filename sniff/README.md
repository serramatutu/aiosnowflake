# Snowflake API sniffing

Snowflake's traditional SQL API is the usual and preferred method of connecting to Snowflake. However, its authentication options are quite limited (only OAuth and key pair), which make it unsuitable for a fully fledged SQL driver.

For this reason, this subproject was created to intercept (sniff) packets coming from the canonical Snowflake Python connector to the Snowflake servers. This way, we can reverse-engineer how their API works to implement a driver.

## Getting started

To start intercepting Snowflake driver requests, you first need to install the sniffing setup (inside the `sniff` folder).

```
# Install Poetry dependencies
python3 -m poetry install

# Install the `mitmproxy` CA certificate to your system.
# NOTE: this will make your system fully trust mitmproxy's CA.
task sniff:install-ca

# Start running the sniffer. This will open a `mitmweb` page in your browser.
task sniff:proxy

# Run Snowflake driver queries through the proxy
task sniff:run-driver -- <args>
```

It is worth noting that the Snowflake driver does not like going through a TLS proxy by default, so if you're running it from a standalone program, be sure to export the following environment vars:
- `HTTP_PROXY=http://localhost:8080`: makes all HTTP requests coming from the driver go through the `mitmproxy` server.
- `HTTPS_PROXY=http://localhost:8080`: same as above but for HTTPS.
- `REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/mitmproxy.crt`: makes the `requests` library (which the canonical Python connector uses internally) trust the self-signed certificate used by `mitmproxy`.

It is also important to run the driver in OCSP fail mode `fail_open`, otherwise it refuses to connect.

If everything goes right, the `mitmweb` interface should show you requests to:
- `http://ocsp.snowflakecomputing.com/ocsp_response_cache.json`
- `https://<account>.snowflakecomputing.com/session/v1/login-request`
- `https://<account>.snowflakecomputing.com/queries/v1/query-request`
- `https://<account>.snowflakecomputing.com/session`

## Endpoints

This section aims to loosely document the Snowflake API, with comments on its behavior. It is probably not complete, but enough to do the job.

### Usual headers

These are the headers the Snowflake Python connector usually sends in:
- `Host: <account>.snowflakecomputing.com`
- `User-Agent: PythonConnector/<connector-version> (<linux-kernel-fully-qualified-name>) CPython/<python-version>`
- `Accept-Encoding: gzip, deflate, br`
- `accept: application/snowflake` (lowercase `accept` for some reason)
- `Connection: keep-alive` (TLS connection needs a heartbeat)
- `Content-Type: application/json`
- `Content-Encoding: gzip`
- `Content-Length: <length>`
- `Authorization: Snowflake Token="<auth-token>"`

It is interesting to note that authentication to the API is done through the `Authorization` header using a `Snowflake Token="<auth-token>"` value.

Sending in `Snowflake Token="None"` or any other value seems to work for unauthenticated endpoints.

### Login: requesting a session token

```
POST https://<account>.snowflakecomputing.com/session/v1/login-request

Parameters:
    [UUID4] request_id
        Appears to be a traditional request ID.
    [UUID4] request_guid
        No idea what it does, but it seems to be another request ID.
```

Driver request body:
```json
{
    "data": {
        "ACCOUNT_NAME": "<account>",
        "CLIENT_APP_ID": "PythonConnector",
        "CLIENT_APP_VERSION": "<connector-version>",
        // Probably for telemetry
        "CLIENT_ENVIRONMENT": {
            "APPLICATION": "PythonConnector",
            "LOGIN_TIMEOUT": 120,
            "NETWORK_TIMEOUT": null,
            "OCSP_MODE": "FAIL_OPEN",
            "OS": "Linux",
            "OS_VERSION": "<linux-kernel-fully-qualified-name>",
            "PYTHON_COMPILER": "GCC 9.4.0",
            "PYTHON_RUNTIME": "CPython",
            "PYTHON_VERSION": "3.11.4",
            "TRACING": 30
        },
        "LOGIN_NAME": "<username>",
        "PASSWORD": "<password>",
        "SESSION_PARAMETERS": {
            "CLIENT_PREFETCH_THREADS": 4
        },
        "SVN_REVISION": null
    }
}
```

Although the driver sends in all that information, the following minimal request body seems to work. All the extra data seems to be for telemetry and/or internal optimizations.
```json
{
    "data": {
        "CLIENT_APP_ID": "aiosnowflake",
        "CLIENT_APP_VERSION": "0.0.1",
        "ACCOUNT_NAME": "<account>",
        "LOGIN_NAME": "<username>",
        "PASSWORD": "<password>"
    }
}
```

Server response:
```json
{
    "code": null,
    "data": {
        "displayUserName": "<username>",
        "firstLogin": true,
        "healthCheckInterval": 45,
        "idToken": null,
        "idTokenValidityInSeconds": 0,
        // This seems to be the token to use for refreshing the session token
        // Resembles an OAuth2 Refresh token.
        "masterToken": "ver:3-hint:...",
        "masterValidityInSeconds": 14400,
        "mfaToken": null,
        "mfaTokenValidityInSeconds": 0,
        "newClientForUpgrade": null,
        // A bunch of session parameters
        "parameters": [
            {
                "name": "CLIENT_PREFETCH_THREADS",
                "value": 4
            },
            {
                "name": "TIMESTAMP_OUTPUT_FORMAT",
                "value": "YYYY-MM-DD HH24:MI:SS.FF3 TZHTZM"
            },
            {
                "name": "TIME_OUTPUT_FORMAT",
                "value": "HH24:MI:SS"
            },
            {
                "name": "TIMESTAMP_TZ_OUTPUT_FORMAT",
                "value": ""
            },
            {
                "name": "CLIENT_RESULT_CHUNK_SIZE",
                "value": 160
            },
            {
                "name": "CLIENT_SESSION_KEEP_ALIVE",
                "value": false
            },
            {
                "name": "QUERY_CONTEXT_CACHE_SIZE",
                "value": 5
            },
            {
                "name": "CLIENT_METADATA_USE_SESSION_DATABASE",
                "value": false
            },
            {
                "name": "CLIENT_OUT_OF_BAND_TELEMETRY_ENABLED",
                "value": false
            },
            {
                "name": "ENABLE_STAGE_S3_PRIVATELINK_FOR_US_EAST_1",
                "value": false
            },
            {
                "name": "CLIENT_RESULT_PREFETCH_THREADS",
                "value": 1
            },
            {
                "name": "TIMESTAMP_NTZ_OUTPUT_FORMAT",
                "value": "YYYY-MM-DD HH24:MI:SS.FF3"
            },
            {
                "name": "CLIENT_METADATA_REQUEST_USE_CONNECTION_CTX",
                "value": false
            },
            {
                "name": "CLIENT_HONOR_CLIENT_TZ_FOR_TIMESTAMP_NTZ",
                "value": true
            },
            {
                "name": "CLIENT_MEMORY_LIMIT",
                "value": 1536
            },
            {
                "name": "CLIENT_TIMESTAMP_TYPE_MAPPING",
                "value": "TIMESTAMP_LTZ"
            },
            {
                "name": "PYTHON_SNOWPARK_USE_SQL_SIMPLIFIER",
                "value": true
            },
            {
                "name": "TIMEZONE",
                "value": "America/Los_Angeles"
            },
            {
                "name": "SNOWPARK_REQUEST_TIMEOUT_IN_SECONDS",
                "value": 86400
            },
            {
                "name": "CLIENT_RESULT_PREFETCH_SLOTS",
                "value": 2
            },
            {
                "name": "CLIENT_TELEMETRY_ENABLED",
                "value": true
            },
            {
                "name": "CLIENT_USE_V1_QUERY_API",
                "value": true
            },
            {
                "name": "CLIENT_DISABLE_INCIDENTS",
                "value": true
            },
            {
                "name": "CLIENT_RESULT_COLUMN_CASE_INSENSITIVE",
                "value": false
            },
            {
                "name": "CSV_TIMESTAMP_FORMAT",
                "value": ""
            },
            {
                "name": "BINARY_OUTPUT_FORMAT",
                "value": "HEX"
            },
            {
                "name": "CLIENT_ENABLE_LOG_INFO_STATEMENT_PARAMETERS",
                "value": false
            },
            {
                "name": "CLIENT_TELEMETRY_SESSIONLESS_ENABLED",
                "value": true
            },
            {
                "name": "CLIENT_FORCE_PROTECT_ID_TOKEN",
                "value": true
            },
            {
                "name": "DATE_OUTPUT_FORMAT",
                "value": "YYYY-MM-DD"
            },
            {
                "name": "CLIENT_CONSENT_CACHE_ID_TOKEN",
                "value": false
            },
            {
                "name": "CLIENT_STAGE_ARRAY_BINDING_THRESHOLD",
                "value": 65280
            },
            {
                // This seems to be important to keep the connection alive.
                // In the original Snowflake connector, it's implemented here:
                // https://github.com/snowflakedb/snowflake-connector-python/blob/d0e00adf07054479df588a384c5598d53047596f/src/snowflake/connector/network.py#L596
                "name": "CLIENT_SESSION_KEEP_ALIVE_HEARTBEAT_FREQUENCY",
                "value": 3600
            },
            {
                "name": "CLIENT_SESSION_CLONE",
                "value": false
            },
            {
                "name": "AUTOCOMMIT",
                "value": true
            },
            {
                "name": "TIMESTAMP_LTZ_OUTPUT_FORMAT",
                "value": ""
            }
        ],
        "remMeToken": null,
        "remMeValidityInSeconds": 0,
        "responseData": null,
        "serverVersion": "7.31.2",
        // Some ID to identify our session. Never seen it used anywhere though...
        "sessionId": 123456,
        "sessionInfo": {
            "databaseName": null,
            "roleName": "<role-name>",
            "schemaName": null,
            "warehouseName": "<warehouse-name>"
        },
        // This is the token that gets sent in the `Authorization` header
        // Resembles an OAuth2 Access token
        "token": "ver:3-hint:...",
        "validityInSeconds": 3600
    },
    "message": null,
    "success": true
}
```

### Creating a SQL query synchronously

```
POST https://<account>.snowflakecomputing.com/queries/v1/query-request

Parameters:
    [UUID4] requestId
        Appears to be a traditional request ID. (Note that it is camelCased for this endpoint, for some weird reason)
    [UUID4] request_guid
        No idea what it does, but it seems to be another request ID. (This one is snake_case)
```

Driver request body:
```json
{
    "asyncExec": false,
    "parameters": {},
    "queryContextDTO": {
        // The first request never has this `entries` field.
        // All subsequent queries have it, with varying timestamp.
        // It does not seem to be important whether we send it or not...
        "entries": [
            {
                "context": {},
                "id": 0,
                "priority": 0,
                // No idea what this timestamp is. If you convert it from
                // UNIX millis, it gives year 3716...
                "timestamp": 37168899888139
            }
        ]
    },
    // Seems to be in the same style as the SQL API
    // See: https://docs.snowflake.com/en/developer-guide/sql-api/submitting-requests#using-bind-variables-in-a-statement
    "bindings": {
        "1": {
            "type": "TEXT",
            "value": "F"
        }
    },
    // Pretty sure it is milliseconds after UNIX Epoch
    "querySubmissionTime": 1694302055389,
    // Looks like the serial order of the queries executed in a session,
    // starting from 1
    "sequenceId": 1,
    "sqlText": "SELECT N_NAME FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION WHERE N_NAME = ? ORDER BY N_NAME"
}
```

### Closing a session

This is executed whenever a connection is closed. Probably invalidates the access/refresh tokens.

```
POST https://<account>.snowflakecomputing.com/session?delete=true

Parameters:
    Note there is no request_id here
    [UUID4] request_guid
        No idea what it does, but it seems to be another request ID. (This one is snake_case)
```

Driver request body:
```json
{}
```
