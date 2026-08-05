from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    phone = models.CharField(max_length=20, blank=True)
    shop_name = models.CharField(max_length=150, blank=True)

    seller_requested = models.BooleanField(default=False)
    seller_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name or self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    FIXED_PRICE = "fixed"
    AUCTION = "auction"

    SALE_TYPE_CHOICES = [
        (FIXED_PRICE, "Direct Price"),
        (AUCTION, "Bidding"),
    ]

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    title = models.CharField(max_length=200)
    caption = models.CharField(max_length=250, blank=True)
    description = models.TextField()

    sale_type = models.CharField(
        max_length=20,
        choices=SALE_TYPE_CHOICES,
        default=FIXED_PRICE,
    )

    # Fixed-price information
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    stock = models.PositiveIntegerField(default=1)

    # Auction information
    starting_bid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    minimum_bid_increment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("10.00"),
    )

    auction_end = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Product media
    image_1 = models.ImageField(upload_to="products/images/")
    image_2 = models.ImageField(
        upload_to="products/images/",
        blank=True,
        null=True,
    )
    image_3 = models.ImageField(
        upload_to="products/images/",
        blank=True,
        null=True,
    )

    video = models.FileField(
        upload_to="products/videos/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        errors = {}

        if self.sale_type == self.FIXED_PRICE:
            if self.price is None:
                errors["price"] = "A direct-price product must have a price."

        if self.sale_type == self.AUCTION:
            if self.starting_bid is None:
                errors["starting_bid"] = (
                    "A bidding product must have a starting bid."
                )

            if self.auction_end is None:
                errors["auction_end"] = (
                    "A bidding product must have an ending date and time."
                )

            if (
                self._state.adding
                and self.auction_end
                and self.auction_end <= timezone.now()
            ):
                errors["auction_end"] = (
                    "The auction ending time must be in the future."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def current_bid(self):
        highest_bid = self.bids.order_by(
            "-amount",
            "-created_at",
        ).first()

        if highest_bid:
            return highest_bid.amount

        return self.starting_bid

    @property
    def minimum_next_bid(self):
        highest_bid = self.bids.order_by(
            "-amount",
            "-created_at",
        ).first()

        if highest_bid:
            return highest_bid.amount + self.minimum_bid_increment

        return self.starting_bid or Decimal("0.00")

    @property
    def auction_is_open(self):
        return (
            self.sale_type == self.AUCTION
            and self.is_active
            and self.auction_end
            and self.auction_end > timezone.now()
        )

    def __str__(self):
        return self.title


class Bid(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="bids",
    )

    bidder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-amount", "-created_at"]

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"


class Order(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (SHIPPED, "Shipped"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"Order #{self.id} - {self.product.title}"