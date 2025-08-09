# Razorpay Payment Gateway Setup

This guide explains how to set up Razorpay payment integration for NIKITA RASOI & BAKES bakery application.

## Overview

The application now supports Razorpay payment gateway, which is one of India's most popular payment providers. It supports:

- **Credit/Debit Cards**: Visa, Mastercard, RuPay, American Express
- **UPI**: Google Pay, PhonePe, BHIM, Paytm UPI, etc.
- **Net Banking**: 50+ banks supported
- **Digital Wallets**: Paytm, Mobikwik, FreeCharge, Ola Money, etc.
- **Cash on Delivery**: Traditional COD with ₹20 handling charges

## Getting Razorpay API Keys (Free Account)

### Step 1: Create Razorpay Account
1. Visit [https://razorpay.com/](https://razorpay.com/)
2. Click "Sign Up" and create a free account
3. Complete email verification and basic KYC
4. For testing, you can use the Test Mode (no KYC required)

### Step 2: Get Test API Keys
1. Login to Razorpay Dashboard
2. Go to "Settings" → "API Keys" 
3. Click "Generate Test Key"
4. Copy both:
   - **Key ID** (starts with `rzp_test_`)
   - **Key Secret** (starts with `rzp_test_`)

### Step 3: Set Environment Variables

#### For Replit:
1. Go to your Replit project
2. Click on "Secrets" tab (lock icon) in the left sidebar
3. Add these secrets:
   - `RAZORPAY_KEY_ID`: Your Razorpay Test Key ID
   - `RAZORPAY_KEY_SECRET`: Your Razorpay Test Key Secret

#### For Local Development:
Create a `.env` file in your project root:
```bash
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_test_key_secret_here
```

## Test Mode vs Live Mode

### Test Mode (Development)
- Use test API keys (starting with `rzp_test_`)
- No real money transactions
- Use test card numbers for testing
- No KYC required

### Test Card Numbers
For testing payments, use these test card details:

**Successful Payment:**
- Card: `4111 1111 1111 1111`
- CVV: Any 3 digits
- Expiry: Any future date

**Failed Payment:**
- Card: `4000 0000 0000 0002`
- CVV: Any 3 digits  
- Expiry: Any future date

### Live Mode (Production)
- Complete business KYC verification
- Use live API keys (starting with `rzp_live_`)
- Real money transactions
- Settlement to your bank account

## Payment Flow

1. **Customer selects items** and goes to checkout
2. **Chooses payment method**: Razorpay or Cash on Delivery
3. **For Razorpay payments**:
   - Razorpay modal opens with payment options
   - Customer completes payment using preferred method
   - Payment is verified server-side
   - Order is created upon successful payment
4. **For Cash on Delivery**:
   - Order is created immediately
   - Payment collected on delivery

## Security Features

- **Server-side Verification**: All payments are verified using Razorpay signatures
- **Secure Sessions**: Payment details stored securely in Flask sessions
- **Error Handling**: Comprehensive error handling for failed payments
- **PCI Compliance**: Razorpay handles all sensitive payment data

## Troubleshooting

### Common Issues:

1. **"Payment Gateway Error"**
   - Check if API keys are correctly set in Replit Secrets
   - Ensure you're using Test keys for development

2. **"Payment Verification Failed"**
   - Check server logs for detailed error messages
   - Verify webhook signature validation

3. **"Razorpay modal not opening"**
   - Check browser console for JavaScript errors
   - Ensure Razorpay SDK is loaded properly

### Testing Checklist:
- [ ] API keys are set in environment variables
- [ ] Test payment with success card number
- [ ] Test payment failure scenario
- [ ] Test Cash on Delivery flow
- [ ] Verify order creation after successful payment
- [ ] Check email confirmations are sent

## Production Deployment

Before going live:

1. **Complete KYC** on Razorpay dashboard
2. **Generate Live API keys** and replace test keys
3. **Test thoroughly** with small amounts
4. **Set up webhooks** for payment notifications (optional)
5. **Configure settlement** schedule in Razorpay dashboard

## Support

- **Razorpay Documentation**: [https://razorpay.com/docs/](https://razorpay.com/docs/)
- **Integration Guide**: [https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/](https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/)
- **Test Cards**: [https://razorpay.com/docs/payments/payments/test-card-details/](https://razorpay.com/docs/payments/payments/test-card-details/)

## Pricing

**Test Mode**: Free
**Live Mode**: 2% transaction fee (standard rate for startups)

*Note: Razorpay offers competitive pricing for businesses. Check their website for current rates and special offers.*