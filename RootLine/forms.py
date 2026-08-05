from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Bid, Product, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


class SellerRequestForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "shop_name",
            "phone",
        ]

        widgets = {
            "shop_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your shop or seller name",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Enter your phone number",
                }
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            "category",
            "title",
            "caption",
            "description",
            "sale_type",
            "price",
            "stock",
            "starting_bid",
            "minimum_bid_increment",
            "auction_end",
            "image_1",
            "image_2",
            "image_3",
            "video",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Product title",
                }
            ),
            "caption": forms.TextInput(
                attrs={
                    "placeholder": "Short product caption",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Describe your product",
                }
            ),
            "auction_end": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "image_1": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
            "image_2": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
            "image_3": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
            "video": forms.ClearableFileInput(
                attrs={
                    "accept": "video/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["auction_end"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "placeholder": "Enter your bid",
                }
            )
        }