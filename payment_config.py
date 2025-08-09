import os
import razorpay
import logging

class RazorpayConfig:
    """Razorpay payment gateway configuration"""
    
    def __init__(self):
        # Use sandbox credentials for testing
        # In production, these should be set via environment variables
        self.key_id = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_demo_key')  # Demo key for testing
        self.key_secret = os.environ.get('RAZORPAY_KEY_SECRET', 'demo_secret')  # Demo secret
        
        # Initialize Razorpay client
        try:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            logging.info("Razorpay client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Razorpay client: {e}")
            self.client = None
    
    def create_order(self, amount, currency='INR', receipt=None, notes=None):
        """Create a Razorpay order"""
        if not self.client:
            logging.error("Razorpay client not initialized")
            return None
            
        try:
            # Amount should be in smallest currency unit (paisa for INR)
            amount_in_paisa = int(amount * 100)
            
            order_data = {
                'amount': amount_in_paisa,
                'currency': currency,
                'receipt': receipt or f'receipt_{int(amount_in_paisa)}',
                'payment_capture': '1'  # Auto capture payment
            }
            
            if notes:
                order_data['notes'] = notes
            
            order = self.client.order.create(data=order_data)
            logging.info(f"Razorpay order created: {order['id']}")
            return order
            
        except Exception as e:
            logging.error(f"Error creating Razorpay order: {e}")
            return None
    
    def verify_payment(self, payment_id, order_id, signature):
        """Verify Razorpay payment signature"""
        if not self.client:
            return False
            
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify signature
            self.client.utility.verify_payment_signature(params_dict)
            logging.info(f"Payment verified successfully: {payment_id}")
            return True
            
        except Exception as e:
            logging.error(f"Payment verification failed: {e}")
            return False
    
    def get_payment_details(self, payment_id):
        """Get payment details from Razorpay"""
        if not self.client:
            return None
            
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logging.error(f"Error fetching payment details: {e}")
            return None

# Initialize Razorpay configuration
razorpay_config = RazorpayConfig()