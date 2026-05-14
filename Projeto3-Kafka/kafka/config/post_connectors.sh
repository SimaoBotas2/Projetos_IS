#!/bin/bash

# Register JDBC source connector (DBInfo from database)
echo "Registering source-dbinfo connector..."
curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://connect:8083/connectors -d @source-dbinfo.json

# Register JDBC sink connectors for each analytics metric
echo "Registering analytics sink connectors..."

curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://connect:8083/connectors -d @sink-revenue-per-book.json
curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://connect:8083/connectors -d @sink-expenses-per-book.json
curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://connect:8083/connectors -d @sink-profit-per-book.json
curl -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://connect:8083/connectors -d @sink-total-revenue.json

echo "Connector registration complete!"
echo "Check status: curl http://connect:8083/connectors"
