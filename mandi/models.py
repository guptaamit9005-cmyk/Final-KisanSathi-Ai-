from django.db import models


class MandiPrice(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    market = models.CharField(max_length=150)

    commodity = models.CharField(max_length=150)

    variety = models.CharField(
        max_length=150,
        blank=True
    )

    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    modal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    arrival_date = models.DateField()

    def __str__(self):
        return f"{self.commodity} - {self.market}"

    class Meta:
        ordering = ["-arrival_date"]