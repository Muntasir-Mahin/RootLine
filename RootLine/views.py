from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    BidForm,
    ProductForm,
    RegisterForm,
    SellerRequestForm,
)
from .models import Bid, Order, Product, Profile


def home(request):
    products = (
        Product.objects.filter(is_active=True)
        .select_related("seller", "category")
    )

    context = {
        "products": products,
    }

    return render(request, "RootLine/home.html", context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)

            login(request, user)

            messages.success(
                request,
                "Your RootLine account has been created.",
            )

            return redirect("buyer_dashboard")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related(
            "seller",
            "category",
        ),
        id=product_id,
    )

    bids = product.bids.select_related("bidder")[:10]

    context = {
        "product": product,
        "bids": bids,
        "bid_form": BidForm(),
    }

    return render(
        request,
        "RootLine/product_detail.html",
        context,
    )


@login_required
def buyer_dashboard(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    orders = (
        Order.objects.filter(buyer=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    bids = (
        Bid.objects.filter(bidder=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    context = {
        "profile": profile,
        "orders": orders,
        "bids": bids,
    }

    return render(
        request,
        "RootLine/buyer_dashboard.html",
        context,
    )


@login_required
def seller_request(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if profile.seller_approved:
        messages.info(
            request,
            "Your seller account is already approved.",
        )
        return redirect("seller_dashboard")

    if request.method == "POST":
        form = SellerRequestForm(
            request.POST,
            instance=profile,
        )

        if form.is_valid():
            seller_profile = form.save(commit=False)
            seller_profile.seller_requested = True
            seller_profile.save()

            messages.success(
                request,
                "Your seller request was submitted. "
                "An admin must approve it.",
            )

            return redirect("buyer_dashboard")
    else:
        form = SellerRequestForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(
        request,
        "RootLine/seller_request.html",
        context,
    )


@login_required
def seller_dashboard(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if not profile.seller_approved:
        messages.error(
            request,
            "Your seller account has not been approved.",
        )

        return redirect("seller_request")

    products = Product.objects.filter(
        seller=request.user
    ).select_related("category")

    received_orders = (
        Order.objects.filter(product__seller=request.user)
        .select_related("buyer", "product")
        .order_by("-created_at")
    )

    context = {
        "profile": profile,
        "products": products,
        "received_orders": received_orders,
    }

    return render(
        request,
        "RootLine/seller_dashboard.html",
        context,
    )


@login_required
def product_create(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if not profile.seller_approved:
        messages.error(
            request,
            "Only approved sellers can list products.",
        )

        return redirect("seller_request")

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            messages.success(
                request,
                "Your product has been listed.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )
    else:
        form = ProductForm()

    return render(
        request,
        "RootLine/product_form.html",
        {"form": form},
    )


@login_required
@require_POST
def place_bid(request, product_id):
    form = BidForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Please enter a valid bid amount.",
        )

        return redirect(
            "product_detail",
            product_id=product_id,
        )

    with transaction.atomic():
        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id,
            sale_type=Product.AUCTION,
            is_active=True,
        )

        if product.seller == request.user:
            messages.error(
                request,
                "You cannot bid on your own product.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )

        if not product.auction_is_open:
            messages.error(
                request,
                "This auction has ended.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )

        amount = form.cleaned_data["amount"]
        minimum_amount = product.minimum_next_bid

        if amount < minimum_amount:
            messages.error(
                request,
                f"Your bid must be at least ৳{minimum_amount}.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )

        Bid.objects.create(
            product=product,
            bidder=request.user,
            amount=amount,
        )

    messages.success(
        request,
        "Your bid was placed successfully.",
    )

    return redirect(
        "product_detail",
        product_id=product_id,
    )


@login_required
@require_POST
def buy_now(request, product_id):
    with transaction.atomic():
        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id,
            sale_type=Product.FIXED_PRICE,
            is_active=True,
        )

        if product.seller == request.user:
            messages.error(
                request,
                "You cannot purchase your own product.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )

        if product.stock < 1:
            messages.error(
                request,
                "This product is out of stock.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )

        if product.price is None:
            messages.error(
                request,
                "This product does not have a valid price.",
            )

            return redirect(
                "product_detail",
                product_id=product.id,
            )

        Order.objects.create(
            buyer=request.user,
            product=product,
            quantity=1,
            unit_price=product.price,
        )

        product.stock -= 1

        if product.stock == 0:
            product.is_active = False

        product.save(
            update_fields=[
                "stock",
                "is_active",
                "updated_at",
            ]
        )

    messages.success(
        request,
        "Order created successfully. Payment will be added later.",
    )

    return redirect("buyer_dashboard")
