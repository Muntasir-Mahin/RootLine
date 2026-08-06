from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Product


class ProductRegressionTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user("seller", password="test-pass")
        self.category = Category.objects.create(name="Food", slug="food")

    def product(self, **overrides):
        values = {
            "seller": self.seller,
            "category": self.category,
            "title": "Honey",
            "description": "Natural honey",
            "sale_type": Product.FIXED_PRICE,
            "price": Decimal("100.00"),
            "image_1": "products/images/honey.png",
        }
        values.update(overrides)
        return Product(**values)

    def test_negative_fixed_price_is_rejected(self):
        product = self.product(price=Decimal("-1.00"))

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_non_positive_auction_amounts_are_rejected(self):
        product = self.product(
            sale_type=Product.AUCTION,
            price=None,
            starting_bid=Decimal("0.00"),
            minimum_bid_increment=Decimal("-1.00"),
            auction_end=timezone.now() + timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_inactive_product_detail_remains_viewable(self):
        product = self.product(stock=0, is_active=False)
        product.full_clean()
        product.save()

        response = self.client.get(
            reverse("product_detail", kwargs={"product_id": product.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This product is out of stock.")
        self.assertNotContains(response, "Buy Now")
