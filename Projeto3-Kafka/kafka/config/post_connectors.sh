#!/bin/bash

BASE_URL="http://connect:8083/connectors"

post() {
    echo "Registering $1..."
    curl -s -X POST -H "Accept:application/json" -H "Content-Type:application/json" $BASE_URL -d @$1
    echo ""
}

# Source connector (DB → Kafka)
post source-dbinfo.json

# Sink connectors — per book (Kafka → PostgreSQL)
post sink-revenue-per-book.json
post sink-expenses-per-book.json
post sink-profit-per-book.json
post sink-avg-purchase-per-book.json
post sink-top-country-sales-per-book.json

# Sink connectors — totals/scalars → total_metrics table
post sink-total-revenue.json
post sink-total-expenses.json
post sink-total-profit.json
post sink-avg-purchase-all.json
post sink-top-profit-book.json

# Sink connectors — windowed → time_window_metrics table
post sink-revenue-last-hour.json
post sink-expenses-last-hour.json

echo ""
echo "All 13 connectors registered!"
echo "Check status: curl http://connect:8083/connectors"
