from confluent_kafka import Producer
import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import socket
import re

class BitcoinPriceProducer:
    def __init__(self):
        conf = {
            'bootstrap.servers': 'localhost:9092',
            'client.id': socket.gethostname()
        }
        self.producer = Producer(conf)
        
    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def get_bitcoin_price(self):
        url = "https://www.coingecko.com/en/coins/bitcoin"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Use the extract_bitcoin_price function
            price = extract_bitcoin_price(response.text)
            if price is not None:
                return price
                
            raise ValueError("Price information not found in page")
            
        except Exception as e:
            print(f"Error fetching Bitcoin price: {e}")
            return None

    def produce_price_updates(self):
        """Continuously produce Bitcoin price updates to Kafka"""
        print("Bitcoin Price Producer Started...")
        
        while True:
            current_price = self.get_bitcoin_price()
            
            if current_price:
                message = {
                    'timestamp': datetime.now().isoformat(),
                    'price': current_price
                }
                
                # Convert message to JSON string
                message_str = json.dumps(message)
                
                # Produce message
                self.producer.produce(
                    'bitcoin-prices',
                    value=message_str.encode('utf-8'),
                    callback=self.delivery_report
                )
                
                # Trigger delivery reports
                self.producer.poll(0)
                
                print(f"Produced: Bitcoin Price ${current_price:,.2f}")
            
            time.sleep(10)  # 5 minutes interval
            
        # Flush any remaining messages
        self.producer.flush()

def extract_bitcoin_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the price span element
    price_element = soup.find('span', {
        'data-converter-target': 'price',
        'data-coin-id': '1'
    })
    
    if price_element:
        # Get the text and clean it up
        price_text = price_element.text
        # Remove $ and , characters and convert to float
        price = float(price_text.replace('$', '').replace(',', ''))
        return price
    
    return None

if __name__ == "__main__":
    producer = BitcoinPriceProducer()
    producer.produce_price_updates() 