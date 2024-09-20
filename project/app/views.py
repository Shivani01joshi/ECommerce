from datetime import datetime
import string
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Category, Order, OrderItem, Product, Shipment, checkoutAddress
from .forms import CategoryForm, CheckoutForm, CustomUserCreationForm, ForgetPasswordForm,  ProductForm, RatingForm, ResetPasswordForm, SearchForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.core.paginator import Paginator
import stripe
from .stripe_utils import create_payment_intent
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
#import razorpay
#razorpay_client=razorpay.Client(auth=(settings.razorpay_id,settings.razorpay_secret))
def home(request):
    form = SearchForm(request.GET or None)
    query = request.GET.get('query')
    products = Product.objects.all() 
    if query:
        products = products.filter(name__icontains=query)
        if not products.exists():
            messages.error(request, "No product found matching your search")
            return render(request,'product_not_found.html')
    
    paginator = Paginator(products, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'form': form, 
        'page_obj': page_obj,
    })


def send_otp(request, email):
    otp = random.randint(100000, 999999)
    request.session['otp'] = str(otp)  
    subject = "Your OTP is"
    message = f"Your OTP is {otp}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    return otp

def Sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            request.session['form_data'] = form.cleaned_data 
            send_otp(request, email)  
            request.session['email'] = email
            return redirect('verify_otp')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        correct_otp = request.session.get('otp')
        if entered_otp == correct_otp:
            form_data = request.session.get('form_data')
            if form_data:
                form = CustomUserCreationForm(form_data)
                if form.is_valid():
                    user = form.save()
                    messages.success(request, 'Account created successfully.')
                    return redirect('login')
                else:
                    messages.error(request, 'Form validation failed.')
            else:
                messages.error(request, 'Form data is missing.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_otp.html')

def verify_otp_login(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        correct_otp = request.session.get('otp')
        username = request.session.get('username')
        password = request.session.get('password')
        if entered_otp == correct_otp:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'OTP verified successfully.')
                return redirect('home')  
            else:
                messages.error(request, 'Authentication failed.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'verify_otp_login.html')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                email = user.email
                request.session['username'] = username
                request.session['password'] = password
                request.session['email'] = email
                send_otp(request, email)
                messages.success(request, 'OTP has been sent to your email.')
                return redirect('verify_otp_login')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def forget_password(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)
            request.session['email'] = email
            send_otp(request, email)
            return redirect('verify_otp_forget_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ForgetPasswordForm()
    return render(request, 'forget_password.html', {'form': form})

def verify_otp_forget_password(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        correct_otp = request.session.get('otp')
        if entered_otp == correct_otp:
            messages.success(request, 'OTP verified successfully.')
            return redirect('Reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp_forget_password')
    else:
        return render(request, 'verify_otp_forget_password.html')
def Reset_password(request):
    if request.method == 'POST':
        email = request.session.get('email')
        user = User.objects.get(email=email)
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('password1')
            new_password2 = form.cleaned_data.get('password1')
            validate_password(new_password, user=user)
            print(new_password)
            if new_password == new_password2:
                user.set_password(new_password)
                user.save()
                # Clear session data after password reset
                messages.success(request, 'Password reset successfully.')
                return redirect('login')
        else:
            return render(request, 'Reset_password.html', {'form': form})
    else:
        form = ResetPasswordForm()
        return render(request, 'Reset_password.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

def change_password(request):
    #print('h1')
    if request.method == 'POST':
        #print('h2')
        form = PasswordChangeForm(user=request.user, data=request.POST)
        #print(request.user.password)
        #print(form)
        #print("Form Data:", request.POST)
        if form.is_valid():
            #print('h3')
            user = form.save()
            #print(user)
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            #print("Form Errors:", form.errors)  # Print form errors
            # Print individual field errors and values
            for field in form:
                print(f"Field: {field.label}, Value: {field.value()}, Errors: {field.errors}")
            messages.error(request, 'Please correct the error below.')
    else:
        #print('h5')
        form = PasswordChangeForm(user=request.user)
    #print('h6')
    return render(request, 'change_password.html', {'form': form})

def product(request):
    object=Product.objects.all()
    return render(request,'home.html',{'object':object})
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CategoryForm()
        return render(request, 'add_category.html', {'form': form})
def add_product(request):
    categories=Category.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        #print(request.FILES)
        #print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('product')
        else:
            return render(request, 'add_product.html', {'form': form,'categories':categories})
    else:
        form = ProductForm()
        return render(request, 'add_product.html', {'form': form,'categories':categories})


def update_product(request, product_id):
    categories=Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'update_product.html', {'form': form, 'product': product,'categories':categories})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product')
    return render(request, 'confirm_delete.html', {'product': product})
@login_required(login_url='login')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    order_item, created = OrderItem.objects.get_or_create(
        user=request.user, 
        product=product, 
        ordered=False
    )
    order_item.quantity += 1
    #print(order_item.quantity)
    order_item.save()
    #print(order_item)
    messages.info(request,"Product added to cart")
    return redirect('product_detail', id=pk) 

def view_cart(request):
    cart_items = OrderItem.objects.filter(user=request.user, ordered=False)
    if request.method == 'POST':
        for item in cart_items:
            quantity_input = request.POST.get(f'quantity_{item.id}')
            if quantity_input is not None:
                item.quantity = int(quantity_input)
                if item.quantity > 0:
                    item.save()
                else:
                    item.delete()  
        return redirect('cart')  
    total_price = sum(item.get_total_item_price() for item in cart_items)
    request.session['total_price']= total_price
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'view_cart.html', context)


def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, user=request.user, ordered=False)
    item.delete() 
    return redirect('cart')

@login_required(login_url='login')
def checkout_page(request):
   # request.session['id'] = id
    profiles = checkoutAddress.objects.filter(user=request.user)
    
    if profiles.exists():
        profile = profiles.first()
    else:
        profile = checkoutAddress(user=request.user)
    
    if request.method == 'POST':
        order_form = CheckoutForm(request.POST, instance=profile)
        
        if order_form.is_valid():
            order_form.save()
            order_items = OrderItem.objects.filter(user=request.user, ordered=False)
            if not order_items.exists():
                return JsonResponse({'error': 'No items in your order'}, status=400)
            return redirect('create_payment_intent')
        else:
            return render(request, 'checkout.html', {'order_form': order_form, 'error': 'Please correct the errors'})
    order_form = CheckoutForm(instance=profile)
    return render(request, 'checkout.html', {'order_form': order_form})

   
    
def create_payment_intent(request):
    if request.method == 'GET':
        try:
            order_items = OrderItem.objects.filter(user=request.user, ordered=False)
            if not order_items.exists():
                return JsonResponse({'error': 'No items in your cart'}, status=400)
            total_amount = sum(item.get_total_item_price() for item in order_items)
            request.session['total_price'] = total_amount  
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),
                currency='usd',
                payment_method_types=['card'],
                payment_method="pm_card_visa",
                metadata={'order_id': 'cart'}
            )
            payment_intent_id = intent.id
            request.session['payment_intent_id'] = payment_intent_id
            client_secret = intent.client_secret
            
            if intent and client_secret:
                return redirect('payment_confirm', payment_intent_id=payment_intent_id)
            else:
                return JsonResponse({'error': 'Failed to create PaymentIntent'}, status=400)
        
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def payment_confirm(request, payment_intent_id):
    return render(request, 'payment_confirm.html', {'payment_intent_id': payment_intent_id})

@login_required(login_url='login')
def confirm_payment(request):
    if request.method == 'POST':
        payment_intent_id = request.session.get('payment_intent_id')

        if not payment_intent_id:
            return JsonResponse({'error': 'No payment intent found'}, status=400)

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            payment_intent.confirm()
            if payment_intent.status == 'succeeded':
                order_items = OrderItem.objects.filter(user=request.user, ordered=False)
                
                print(order_items)
                if not order_items.exists():
                    return JsonResponse({'error': 'No items found in your cart'}, status=400)
                try:
                    order = Order.objects.filter(user=request.user, ordered=False)
                    order.order_id = payment_intent.id
                    order.datetime_ofpayment = datetime.fromtimestamp(payment_intent.created)
                except Order.DoesNotExist:
                    order = Order.objects.create(
                        user=request.user,
                        ordered=False,
                        order_id=payment_intent.id,
                        datetime_ofpayment=datetime.fromtimestamp(payment_intent.created)
                    )
                print(order)
                order = Order.objects.create(
                        user=request.user,
                        ordered=False,
                        order_id=payment_intent.id,
                        datetime_ofpayment=datetime.fromtimestamp(payment_intent.created)
                    )
                for item in order_items:
                    item.ordered = True
                    item.save()  
                order_details = []
                for item in order_items:
                    order_name = item.product.name 
                    quantity = item.quantity
                    order_details.append(f"Order Name: {order_name}, Quantity: {quantity}")
                order_details_str = "\n".join(order_details)
                order.items.set(order_items)
                #print(order.items)
                order.save()
                order_items.delete()
                tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

                # Create or update shipment details
                shipment, _ = Shipment.objects.get_or_create(
                    order=order,
                    defaults={
                        'tracking_number': tracking_number,
                        'shipped_at': timezone.now(),
                        'shipment_status': 'Pending'
                    }
                )
                shipment.shipped_at = timezone.now()  # Update shipped_at
                shipment.delivered_at = timezone.now() if shipment.shipment_status == 'Shipped' else shipment.delivered_at
                shipment.save()
                print(shipment)
                total_price = request.session.get('total_price')
                subject = "Payment status"
                html_message = render_to_string('order_confirmation_email.html', {
                    'total_price': total_price,
                    'order_details': order_details_str,
                    'customer_name': request.user, 
                })
                plain_message = strip_tags(html_message)

                #message = f"Your Order has been Confirmed,Your transaction has been successfully completed. The total amount is Rs.{total_price}, and the items you have purchased are as follows: {order_details_str}. They will be delivered in 2 days."
                from_email = 'svjoshi885@gmail.com'
                recipient_list = [request.user.email]
                send_mail(subject, plain_message, from_email, recipient_list)

                return render(request, 'payment_success.html') 

            else:
                return redirect('payment_failed') 

        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




@login_required(login_url='login')
def user_orders(request):
    orders = Order.objects.all()
    context = {
        'orders': orders
    }
    return render(request, 'user_orders.html', context)

def shippment_status(request,id):
    order = get_object_or_404(Order, id=id)
    shipment = getattr(order, 'shipment', None)
    context = {
        'order': order,
        'shipment': shipment,
    }
    return render(request, 'shipment_details.html', context)

@login_required(login_url='login')
def particular_orders(request):
    orders = Order.objects.filter(user=request.user)
    #print(orders)
    context = {
        'orders': orders
    }
    return render(request, 'user_orders.html', context)

def cancel_payment(request):
    return render(request,'cancel_payment.html')

def product_detail(request, id):
    #print('hi')
    product = get_object_or_404(Product, id=id)
    #print(product_id)
    reviews = product.reviews.all()  # Related name 'reviews' from the Rating model

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = RatingForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'get_product.html', context)

def scan_order(request):
    if request.method == 'POST':
        scanned_code = request.POST.get('tracking_number')

        try:
            shipment = get_object_or_404(Shipment, tracking_number=scanned_code)
            
            # Update shipment status based on input from the scanner
            if shipment.shipment_status == 'Pending':
                shipment.mark_as_shipped()
                shipment.shipped_at = timezone.now()  # Update shipped_at when marked as shipped
                shipment.save()  # Save the shipment
                messages.success(request, f"Order {shipment.order.order_id} marked as shipped.")
                return redirect('home')

            elif shipment.shipment_status == 'Shipped':
                shipment.delivered_at = timezone.now()  # Directly set delivered_at
                shipment.mark_as_delivered()  # Call to change status
                shipment.save()  # Save the shipment
                messages.success(request, f"Order {shipment.order.order_id} marked as delivered.")
                return redirect('home')

            else:
                messages.success(request, "Order has already been delivered.")
                return redirect('home')
                
        except Shipment.DoesNotExist:
            return HttpResponse("Invalid tracking number.")
    
    return render(request, 'scan_order.html')
'''
@login_required(login_url='login')
def addresss(request):
    orders = checkoutAddress.objects.get(user=request.user)
    #print(orders)
    #print(orders.street_address)
    return render(request, 'address.html', {'profile':orders})

def product_list(request):
    form = SearchForm(request.GET or None)
    query = request.GET.get('query')
    if query:
        products = Product.objects.filter(name__icontains=query)  # Adjust the filter as needed
    else:
        products = Product.objects.all()
    return render(request, 'home.html', {'object': products, 'form': form})
    '''