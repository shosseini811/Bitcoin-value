from confluent_kafka import Consumer, KafkaError
import json
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BitcoinPriceConsumer:
    def __init__(self):
        # Kafka Consumer configuration
        conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'bitcoin_price_group',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
            'socket.timeout.ms': 3000,         # Adjusted to avoid blocking
            'session.timeout.ms': 10000,
            'max.poll.interval.ms': 300000,
            'fetch.wait.max.ms': 2000          # Ensured fetch.wait.max.ms < socket.timeout.ms - 1000ms
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(['bitcoin-prices'])

        # Twilio setup
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )

    def send_whatsapp(self, message):
        """Send WhatsApp message using Twilio"""
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
                to=f"whatsapp:{os.getenv('TARGET_WHATSAPP_NUMBER')}"
            )
            print(f"WhatsApp message sent: {message.sid}")
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")

    def process_messages(self):
        """Process incoming messages from Kafka"""
        print("Bitcoin Price Consumer Started...")

        try:
            while True:
                msg = self.consumer.poll(0.1)  # Poll frequently (100ms)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        break

                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    current_price = data.get('price')
                    timestamp = data.get('timestamp')

                    if current_price is None or timestamp is None:
                        print("Incomplete data received.")
                        continue

                    print(f"Received: Bitcoin Price ${current_price:,.2f} at {timestamp}")

                    # Construct the WhatsApp message
                    alert_msg = (
                        f"📈 Bitcoin Price Update\n"
                        f"Timestamp: {timestamp}\n"
                        f"Current Price: ${current_price:,.2f}"
                    )
                    self.send_whatsapp(alert_msg)

                except json.JSONDecodeError as e:
                    print(f"Error decoding message: {e}")
                    continue

        except KeyboardInterrupt:
            print("Stopping Bitcoin Price Consumer...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    consumer = BitcoinPriceConsumer()
    consumer.process_messages() 