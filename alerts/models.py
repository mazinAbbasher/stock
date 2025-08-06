from django.db import models
from django.conf import settings

class StockPrice(models.Model):
    symbol = models.CharField(max_length=10, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.symbol} - {self.price} @ {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('threshold', 'Threshold'),
        ('duration', 'Duration'),
    ]
    CONDITION_CHOICES = [
        ('above', 'Above'),
        ('below', 'Below'),
    ]
    STOCK_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "META", "NVDA", "NFLX", "INTC", "AMD"
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    symbol = models.CharField(max_length=10, db_index=True, choices=[(symbol, symbol) for symbol in STOCK_SYMBOLS])
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    condition = models.CharField(max_length=5, choices=CONDITION_CHOICES)
    target_price = models.DecimalField(max_digits=12, decimal_places=4)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)  # Only for duration alerts
    start_time = models.DateTimeField(null=True, blank=True)  # For duration alerts
    created_at = models.DateTimeField(auto_now_add=True)
    triggered = models.BooleanField(default=False, db_index=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.symbol} {self.alert_type} {self.condition} {self.target_price}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'symbol', 'triggered']),
        ]
