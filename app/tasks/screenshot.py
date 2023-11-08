import logging

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from app.logic.screenshot import crawl_and_screenshot
from db.core import get_sync_db
from app.config import settings
from dramatiq import set_broker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the RabbitMQ broker with your specific URL
rabbitmq_broker = RabbitmqBroker(url=settings.broker_url)

# Set the broker for Dramatiq to use
set_broker(rabbitmq_broker)


@dramatiq.actor(max_retries=5, min_backoff=1000)
def take_screenshots_task(start_url, number_of_links, unique_id):
    # Synchronous database session
    for db in get_sync_db():
        try:
            results = crawl_and_screenshot(start_url, number_of_links, unique_id, db)
            return results
        except Exception as e:
            logger.exception(f"An error occurred while taking screenshots: {e}")
            raise
        finally:
            db.close()
