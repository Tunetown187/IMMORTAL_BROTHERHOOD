import stripe
import logging
from typing import Dict, Optional
import streamlit as st
import base64

class PaymentHandler:
    def __init__(self):
        self.setup_logging()
        self.setup_stripe()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_stripe(self):
        """Initialize Stripe with API keys"""
        try:
            # Get API keys from Streamlit secrets
            stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
            self.publishable_key = st.secrets["STRIPE_PUBLISHABLE_KEY"]
            self.logger.info("Stripe initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Stripe: {str(e)}")
            raise

    async def create_product(self, name: str, description: str, price: float) -> Dict:
        """Create a Stripe product with price"""
        try:
            # Create product
            product = stripe.Product.create(
                name=name,
                description=description
            )
            
            # Create price for the product
            price_obj = stripe.Price.create(
                product=product.id,
                unit_amount=int(price * 100),  # Convert to cents
                currency="usd",
                recurring={"interval": "month"}  # For subscription products
            )
            
            return {
                "product_id": product.id,
                "price_id": price_obj.id,
                "name": name,
                "price": price
            }
            
        except Exception as e:
            self.logger.error(f"Error creating product: {str(e)}")
            return None

    async def create_checkout_session(self, price_id: str, success_url: str, cancel_url: str) -> Optional[str]:
        """Create a Stripe checkout session"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            return session.url
            
        except Exception as e:
            self.logger.error(f"Error creating checkout session: {str(e)}")
            return None

    async def handle_subscription(self, subscription_id: str) -> Dict:
        """Handle subscription updates"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "customer": subscription.customer
            }
            
        except Exception as e:
            self.logger.error(f"Error handling subscription: {str(e)}")
            return None

    async def create_customer(self, email: str, payment_method: str) -> Optional[str]:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method,
                invoice_settings={
                    'default_payment_method': payment_method
                }
            )
            
            return customer.id
            
        except Exception as e:
            self.logger.error(f"Error creating customer: {str(e)}")
            return None

    async def process_refund(self, payment_intent: str, amount: Optional[int] = None) -> bool:
        """Process a refund"""
        try:
            refund = stripe.Refund.create(
                payment_intent=payment_intent,
                amount=amount  # If None, full amount will be refunded
            )
            
            return refund.status == "succeeded"
            
        except Exception as e:
            self.logger.error(f"Error processing refund: {str(e)}")
            return False

    async def get_payment_methods(self, customer_id: str) -> list:
        """Get customer's saved payment methods"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [{
                "id": pm.id,
                "brand": pm.card.brand,
                "last4": pm.card.last4,
                "exp_month": pm.card.exp_month,
                "exp_year": pm.card.exp_year
            } for pm in payment_methods.data]
            
        except Exception as e:
            self.logger.error(f"Error getting payment methods: {str(e)}")
            return []

    async def create_invoice(self, customer_id: str, items: list) -> Optional[str]:
        """Create and send an invoice"""
        try:
            # Create invoice items
            for item in items:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    price=item['price_id'],
                    quantity=item.get('quantity', 1)
                )
            
            # Create and send invoice
            invoice = stripe.Invoice.create(
                customer=customer_id,
                auto_advance=True,  # Auto-finalize and send the invoice
            )
            
            return invoice.id
            
        except Exception as e:
            self.logger.error(f"Error creating invoice: {str(e)}")
            return None

    async def get_account_balance(self) -> Dict:
        """Get current account balance"""
        try:
            balance = stripe.Balance.retrieve()
            
            return {
                "available": [{
                    "amount": b.amount / 100,  # Convert from cents
                    "currency": b.currency
                } for b in balance.available],
                "pending": [{
                    "amount": b.amount / 100,
                    "currency": b.currency
                } for b in balance.pending]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting balance: {str(e)}")
            return None