from twilio.rest import Client
import os
from dotenv import load_dotenv

def test_whatsapp_message():
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize Twilio client
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        # Send test message
        message = client.messages.create(
            body='🚀 chetri Pooneh che khabara',
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
            to=f"whatsapp:{os.getenv('TARGET_WHATSAPP_NUMBER')}"
        )
        
        print(f"Success! Message SID: {message.sid}")
        print("Check your WhatsApp for the test message!")
        
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your .env file has all required variables")
        print("2. Ensure you've joined the Twilio WhatsApp sandbox")
        print("3. Check if your Twilio account is active and has credit")
        print("4. Verify your WhatsApp number is correct with country code")

if __name__ == "__main__":
    print("Sending test WhatsApp message...")
    test_whatsapp_message() 