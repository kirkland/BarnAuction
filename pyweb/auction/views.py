from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Count, Min, Sum, Avg

# Create your views here.

from django.http import HttpResponse
from auction.models import Customer, Item, Transaction
#from auction.forms import CheckoutForm
def index(request):
    if request.POST:
        try:
            c = Customer.objects.get(paddle_number=request.POST['pn'])
        except :
            return HttpResponse("Invalid paddle number");
        transactions = c.transaction_set.all()
        if transactions:
            transaction_sum = c.transaction_set.aggregate(Sum('price'))['price__sum']
        else:
            transaction_sum = 0
        return render(request, 'auction/simplebill.html', {'customer':c, 'transactions': transactions, 'transaction_sum': transaction_sum})

    else:
        return render(request,'auction/index.html')


    
def bill(request):
    if 'id' in request.GET:
        c = Customer.objects.get(pk=request.GET['id'])
        transactions = c.transaction_set.all()
        if transactions:
            transaction_sum = c.transaction_set.aggregate(Sum('price'))['price__sum']
        else:
            transaction_sum = 0
        if not c.paid_amount :
            return HttpResponse("Cannot checkout as paid amount is zero.")

        return render(request, 'auction/bill.html', {'customer':c, 'transactions': transactions, 'transaction_sum': transaction_sum, 'balance': transaction_sum - c.paid_amount})
    else:
        return HttpResponse( "id not found");


def winners(request):
    return render(request, 'auction/winners.html', {'transactions': Transaction.objects.filter(item__type='SILIENT').order_by('customer__paddle_number') } )
