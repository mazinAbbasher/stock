from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
import logging
from .services import fetch_stock_prices, check_threshold_alert, evaluate_duration_alert, STOCK_SYMBOLS
from .models import StockPrice, Alert

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_store_and_check_alerts(self):
    try:
        data = fetch_stock_prices()
        if not data:
            logging.warning("No stock price data fetched.")
            return

        # Store prices in DB
        stock_objs = [
            StockPrice(symbol=item["symbol"], price=item["price"])
            for item in data if "symbol" in item and "price" in item
        ]
        if stock_objs:
            StockPrice.objects.bulk_create(stock_objs)
            logging.info(f"Stored {len(stock_objs)} stock prices.")
        else:
            logging.warning("No valid stock price objects to store.")
            return

        symbol_price_map = {item["symbol"]: item["price"] for item in data if "symbol" in item and "price" in item}

        # Use select_related to avoid extra DB queries for user
        alerts = Alert.objects.filter(triggered=False).select_related('user')
        triggered_alerts = []
        email_messages = []

        for alert in alerts:
            latest_price = symbol_price_map.get(alert.symbol)
            if latest_price is None:
                continue
            triggered = False
            if alert.alert_type == 'threshold':
                triggered = check_threshold_alert(alert, latest_price)
            elif alert.alert_type == 'duration':
                triggered = evaluate_duration_alert(alert, latest_price)
            if triggered:
                alert.triggered = True
                alert.triggered_at = timezone.now()
                triggered_alerts.append(alert)
                if alert.user.email:
                    alert_type = alert.get_alert_type_display()
                    condition = alert.get_condition_display()
                    duration = (
                        f" over a period of {alert.duration_minutes} minutes"
                        if alert.alert_type == 'duration' and alert.duration_minutes else ""
                    )
                    triggered_at_str = timezone.localtime(alert.triggered_at).strftime('%Y-%m-%d %H:%M:%S')
                    email_messages.append({
                        "subject": f"Stock Alert Notification: {alert.symbol}",
                        "message": (
                            f"Hello {alert.user.get_full_name() or alert.user.username},\n\n"
                            f"We are writing to inform you that your stock alert for {alert.symbol} has been triggered.\n\n"
                            f"Alert summary:\n"
                            f"Your alert was set to notify you when the price of {alert.symbol} "
                            f"was {condition.lower()} {alert.target_price}{duration}. "
                            f"At {triggered_at_str}, the latest price reached {latest_price}, "
                            f"which met your alert criteria ({alert_type} alert).\n\n"
                            f"You can log in to your account to review this alert or set up new ones as needed.\n\n"
                            f"Thank you for trusting us to monitor your stocks. If you have any questions or need assistance, "
                            f"please don't hesitate to contact our support team.\n\n"
                            f"Best regards,\n"
                            f"The Stock Alerts Team"
                        ),
                        "recipient": alert.user.email
                    })

        # Bulk update triggered alerts
        if triggered_alerts:
            Alert.objects.bulk_update(triggered_alerts, ["triggered", "triggered_at"])
            logging.info(f"Triggered {len(triggered_alerts)} alerts.")

        # Send emails (individually for reliability)
        for msg in email_messages:
            try:
                send_mail(
                    subject=msg["subject"],
                    message=msg["message"],
                    from_email=None,
                    recipient_list=[msg["recipient"]],
                    fail_silently=False,
                )
                logging.info(f"Alert email sent to {msg['recipient']}")
            except Exception as e:
                logging.error(f"Email send failed: {e}")

    except Exception as e:
        logging.error(f"Error in fetch_store_and_check_alerts: {e}")
        self.retry(exc=e)
