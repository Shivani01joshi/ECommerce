from django.utils import timezone
from django_countries.fields import CountryField
from django.db.models import Avg
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): 
        return self.name 
    
class Product(models.Model):
    name = models.CharField(max_length=60) 
    price = models.IntegerField(default=0) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1) 
    description = models.CharField( 
        max_length=250, default='', blank=True, null=True) 
    image = models.ImageField(upload_to='products/') 

    def average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 2) if average else 0  
    
class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)  

    def __str__(self):
        return self.review

    
class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    ordered=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def get_total_item_price(self):
        return self.quantity*self.product.price
    
    def final_price(self):
        return self.get_total_item_price()
    
class checkoutAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country=CountryField (multiple=False)
    zip_code=models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items=models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now=True)
    order_date=models.DateTimeField(auto_now_add=True)
    ordered=models.BooleanField(default=False)
    order_id=models.CharField(max_length=100,blank=True,null=True,unique=True,default=None)
    datetime_ofpayment=models.DateTimeField(auto_now_add=True)
    order_delivered=models.BooleanField(default=False)
    order_received=models.BooleanField(default=False)
    checkout_address = models.ForeignKey(checkoutAddress, on_delete=models.SET_NULL, null=True) 
    def __str__(self):
        return f"Order {self.order_id} by {self.user}"
    
    def get_total_order_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())
    
    def get_total_count(self):
        order=Order.objects.get(id=self.pk)
        return order.items.count()
class Shipment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, unique=True,blank=True)  
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    edd = models.DateTimeField(null=True, blank=True) 
    shipment_status = models.CharField(max_length=20, default='Pending')  # Pending, Shipped, Delivered
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return f"Shipment {self.tracking_number} for Order {self.order.order_id}"

    def mark_as_shipped(self):
        self.shipment_status = 'Shipped'
        self.shipped_at = timezone.now()
        self.order.order_delivered = False  # The order is in transit
        self.order.save()
        self.save()

    def mark_as_delivered(self):
        self.shipment_status = 'Delivered'
        self.delivered_at = timezone.now()
        self.order.order_delivered = True  # Order has been delivered
        self.order.save()
        self.save()
    
    def set_dimensions(self, length, breadth, weight):
        # Store dimensions as a formatted string
        self.dimensions = f"Length: {length} cm, Breadth: {breadth} cm, Weight: {weight} kg"
        self.save()

    def get_dimensions(self):
        # Split dimensions back into individual components (optional)
        return self.dimensions.split(", ")


