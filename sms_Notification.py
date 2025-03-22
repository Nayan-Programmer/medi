import os
import logging

# Try to import Twilio, but handle the case where it's not available
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio package not available. SMS functionality will be disabled.")

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def are_twilio_credentials_available():
    """
    Check if all Twilio credentials are available in environment variables
    
    Returns:
        bool: True if all credentials are available, False otherwise
    """
    return TWILIO_AVAILABLE and all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER])

def send_sms_notification(to_phone_number, message):
    """
    Send SMS notification using Twilio
    
    Args:
        to_phone_number (str): The recipient's phone number in E.164 format
        message (str): The message to send
        
    Returns:
        tuple: (bool, str) - (success status, error message if any)
    """
    # Check if Twilio is available
    if not TWILIO_AVAILABLE:
        error_msg = "Twilio package is not installed"
        logging.error(error_msg)
        return False, error_msg
    
    # Check if Twilio credentials are available
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        error_msg = "Twilio credentials not found in environment variables"
        logging.error(error_msg)
        return False, error_msg
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        
        logging.info(f"SMS notification sent successfully. SID: {message.sid}")
        return True, ""
    
    except TwilioRestException as e:
        error_msg = f"Twilio error: {str(e)}"
        logging.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Error sending SMS: {str(e)}"
        logging.error(error_msg)
        return False, error_msg

def generate_notification_message(diagnosis_data):
    """
    Generate notification message based on diagnosis data
    
    Args:
        diagnosis_data (dict): Diagnosis data including disease, risk level, etc.
        
    Returns:
        str: Formatted notification message
    """
    disease = diagnosis_data.get('disease', 'Unknown condition')
    risk_level = diagnosis_data.get('risk_level', 'unknown').upper()
    
    # Create custom messages based on risk level
    if risk_level == 'HIGH':
        message = (f"URGENT HEALTH ALERT: Your symptoms indicate {disease} with {risk_level} risk. "
                  f"Please seek immediate medical attention.")
    elif risk_level == 'MODERATE':
        message = (f"HEALTH ALERT: Your symptoms indicate {disease} with {risk_level} risk. "
                  f"Consider consulting a healthcare provider soon.")
    else:
        message = (f"HEALTH NOTIFICATION: Your symptoms indicate {disease} with {risk_level} risk. "
                  f"Monitor your symptoms and seek medical advice if they worsen.")
        
    # Add disclaimer
    message += " This is an automated message from MediDiagnose. Not a substitute for professional medical advice."
    
    return message
