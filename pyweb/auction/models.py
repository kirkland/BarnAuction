from django.db import models

# Create your models here.

from django.db import models

class Customer(models.Model):
    paddle_number = models.IntegerField(unique=True)
#    access_code = models.IntegerField()
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    paid = models.BooleanField(help_text="This will be checked automatically during checkout")
    paid_amount = models.DecimalField(max_digits=7,decimal_places=2, null = True, blank = True, help_text="Leave this field blank if paid in full ")
    modified_time = models.DateTimeField(auto_now = True)
    PAYMENT_METHODS = ( ('CASH', 'Cash'), ('CHECK', 'Check'), ('CREDITCARD', 'CreditCard'), ('OTHER', 'Other'),)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, null = True, blank= True, help_text = "Select a payment method during checkout")
    email_receipt = models.BooleanField()
    def __unicode__(self):
        return "%s %s" % (self.paddle_number, self.name)
    class Meta:
        ordering = ['paddle_number']

class Item(models.Model):
    bid_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    max_winner = models.IntegerField(default = 1)
    TYPES = ( ('SILIENT', 'Slient Auction'), ('LIVE', 'Live Auction'),  ('OTHER', 'Other'),)
    type = models.CharField(max_length = 10, choices = TYPES);
    created_time = models.DateTimeField(auto_now_add = True)
    modified_time = models.DateTimeField(auto_now = True)
    def __unicode__(self):
        return "%s(%s)" % (self.name, self.bid_number)
    class Meta:
        ordering = ['bid_number']
   
class Transaction(models.Model):
    customer = models.ForeignKey(Customer)
    item = models.ForeignKey(Item)
    price = models.DecimalField(max_digits=7,decimal_places=2)
    created_time = models.DateTimeField(auto_now_add = True)
    modified_time = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ['customer__paddle_number']
    def __unicode__(self):
        return "%s(%d) purchased %s(%s) at %f" % (self.customer.name, self.customer.paddle_number, self.item.name, self.item.bid_number, self.price)

