#!/bin/bash

BASE_URL="http://connect:8083/connectors"

delete_if_exists() {
    name=$1
    status=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/$name)
    if [ "$status" = "200" ]; then
        echo "  Deleting existing $name..."
        curl -s -X DELETE $BASE_URL/$name
        sleep 1
    fi
}

post() {
    file=$1
    name=$(grep '"name"' $file | head -1 | sed 's/.*"name": *"\([^"]*\)".*/\1/')
    echo "Registering $name..."
    delete_if_exists $name
    curl -s -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
        $BASE_URL -d @$file | grep -q '"name"' && echo "  ✓ OK" || echo "  ✗ FAILED"
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
post sink-profit-last-hour.json

echo ""
echo "All 14 connectors registered!"
echo "Check status: curl http://connect:8083/connectors"
