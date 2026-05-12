#!/bin/bash

# Simple script to run all components in background with logging
# Uses fat JAR with dependencies included

WORKSPACE="/workspace"
LOG_DIR="/workspace/logs"

# Create logs directory
mkdir -p $LOG_DIR

echo "Starting Kafka Project 3 components..."
echo ""

# Kill any existing processes
pkill -f "PurchaseEventProducer" 2>/dev/null
pkill -f "SaleEventProducer" 2>/dev/null
pkill -f "ProjetoBase3Streams" 2>/dev/null

sleep 1

# Start PurchaseEventProducer
echo "[1/3] Starting PurchaseEventProducer..."
cd $WORKSPACE
java -cp target/project3-jar-with-dependencies.jar is.project3.PurchaseEventProducer > $LOG_DIR/purchase.log 2>&1 &
PID_PURCHASE=$!
echo "      PID: $PID_PURCHASE (log: $LOG_DIR/purchase.log)"

# Start SaleEventProducer
echo "[2/3] Starting SaleEventProducer..."
java -cp target/project3-jar-with-dependencies.jar is.project3.SaleEventProducer > $LOG_DIR/sales.log 2>&1 &
PID_SALES=$!
echo "      PID: $PID_SALES (log: $LOG_DIR/sales.log)"

# Start ProjetoBase3Streams
echo "[3/3] Starting ProjetoBase3Streams..."
java -cp target/project3-jar-with-dependencies.jar is.project3.ProjetoBase3Streams > $LOG_DIR/streams.log 2>&1 &
PID_STREAMS=$!
echo "      PID: $PID_STREAMS (log: $LOG_DIR/streams.log)"

echo ""
echo "All components started in background"
echo ""
echo "PIDs:"
echo "  Purchase: $PID_PURCHASE"
echo "  Sales:    $PID_SALES"
echo "  Streams:  $PID_STREAMS"
echo ""
echo "Monitor logs:"
echo "  tail -f $LOG_DIR/purchase.log   # Watch purchase producer"
echo "  tail -f $LOG_DIR/sales.log      # Watch sales producer"
echo "  tail -f $LOG_DIR/streams.log    # Watch Kafka Streams processor"
echo ""
echo "Monitor Kafka Results topic:"
echo "  kafka-console-consumer.sh --bootstrap-server broker1:9092 --topic Results --from-beginning"
echo ""
echo "Stop all:"
echo "  kill $PID_PURCHASE $PID_SALES $PID_STREAMS"
echo "  or: pkill -f PurchaseEventProducer; pkill -f SaleEventProducer; pkill -f ProjetoBase3Streams"
