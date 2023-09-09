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
task sniff:run-driver <args>
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
