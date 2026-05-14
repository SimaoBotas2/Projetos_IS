"""
Kafka producer for sending Purchase and Sale events.
"""

import json
import time
from kafka import KafkaProducer
from app.models import PurchaseEvent, SaleEvent

# Kafka configuration
BOOTSTRAP_SERVERS = ["localhost:29092"]


class EventProducer:
    """Produces events to Kafka topics."""

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )

    def send_purchase_event(self, book_id: int, supplier_id: int, cost: float, quantity: int) -> dict:
        """
        Send a purchase event to the Purchases topic.

        Args:
            book_id: ID of the book being purchased
            supplier_id: ID of the supplier
            cost: Cost per unit
            quantity: Quantity purchased

        Returns:
            Dictionary with event details and confirmation
        """
        event = {
            "book_id": book_id,
            "supplier_id": supplier_id,
            "cost": float(cost),
            "quantity": int(quantity),
            "timestamp": int(time.time() * 1000)
        }

        try:
            future = self.producer.send('Purchases', value=event)
            record_metadata = future.get(timeout=10)

            return {
                "status": "success",
                "message": f"Purchase event sent for book {book_id}",
                "event": event,
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send purchase event: {str(e)}",
                "event": event
            }

    def send_sale_event(self, book_id: int, country_id: int, price: float, quantity: int) -> dict:
        """
        Send a sale event to the Sales topic.

        Args:
            book_id: ID of the book being sold
            country_id: ID of the country where the sale occurred
            price: Price per unit
            quantity: Quantity sold

        Returns:
            Dictionary with event details and confirmation
        """
        event = {
            "book_id": book_id,
            "country_id": country_id,
            "price": float(price),
            "quantity": int(quantity),
            "timestamp": int(time.time() * 1000)
        }

        try:
            future = self.producer.send('Sales', value=event)
            record_metadata = future.get(timeout=10)

            return {
                "status": "success",
                "message": f"Sale event sent for book {book_id}",
                "event": event,
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send sale event: {str(e)}",
                "event": event
            }

    def send_purchase_events_batch(self, purchases: list) -> dict:
        """
        Send multiple purchase events in batch.

        Args:
            purchases: List of dicts with keys: book_id, supplier_id, cost, quantity

        Returns:
            Dictionary with batch results
        """
        results = []
        for purchase in purchases:
            result = self.send_purchase_event(
                book_id=purchase["book_id"],
                supplier_id=purchase["supplier_id"],
                cost=purchase["cost"],
                quantity=purchase["quantity"]
            )
            results.append(result)

        self.producer.flush()

        return {
            "status": "success",
            "message": f"Sent {len(results)} purchase events",
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }

    def send_sale_events_batch(self, sales: list) -> dict:
        """
        Send multiple sale events in batch.

        Args:
            sales: List of dicts with keys: book_id, country_id, price, quantity

        Returns:
            Dictionary with batch results
        """
        results = []
        for sale in sales:
            result = self.send_sale_event(
                book_id=sale["book_id"],
                country_id=sale["country_id"],
                price=sale["price"],
                quantity=sale["quantity"]
            )
            results.append(result)

        self.producer.flush()

        return {
            "status": "success",
            "message": f"Sent {len(results)} sale events",
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }

    def close(self):
        """Close the producer."""
        self.producer.close()


# Global producer instance
_producer = None


def get_producer() -> EventProducer:
    """Get or create the global producer instance."""
    global _producer
    if _producer is None:
        _producer = EventProducer()
    return _producer
