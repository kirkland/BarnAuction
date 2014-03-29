from django.contrib import admin
from django.http import Http404, HttpResponseRedirect
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.contrib import messages
# Register your models here.
from django.shortcuts import redirect
from django.db.models import Count, Min, Sum, Avg
from django.contrib import admin
from auction.models import Customer
from auction.models import Item
from auction.models import Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    can_delete = False
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return obj.max_winner - len(obj.transaction_set.all())
        return 0
    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            return obj.max_winner
        return 0
    template = 'admin/item-transaction-inline.html'


class CustomerAdmin(admin.ModelAdmin):
    list_display = ( 'paddle_number', 'name',   'paid', 'payment_method', 'paid_amount', 'email')
    search_fields = ['paddle_number', 'name']
    list_filter = ['paid', 'email_receipt']
#    exclude = ['paid', 'payment_method',]
#    readonly_fields = ['paddle_number', ]
    fields = ['paddle_number', 'name', 'email', 'email_receipt', 'payment_method',  'paid_amount', 'paid' ]
    list_display_links = ['paddle_number', 'name']
    def get_actions(self, request):
        return []
    change_form_template = "auction/change_form.html"

    def change_view(self,request, object_id, form_url='', extra_context=None):
        r= super(CustomerAdmin, self).change_view(request, object_id=object_id, form_url = form_url, extra_context=extra_context)
        if hasattr(r, 'context_data'):
            c = r.context_data['original']
            r.context_data['transactions'] = c.transaction_set.all()
            r.context_data['transaction_sum'] = c.transaction_set.aggregate(Sum('price'))['price__sum']
        return r

    def response_change(self, request, obj):
        opts = self.model._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        msg_dict = {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}
        if "_checkout" in request.POST:
            msg = _('%(name)s "%(obj)s" was checkout successfully. You may print receipt below.') % msg_dict
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path + "?show_print=True"
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        return super(CustomerAdmin, self).response_change(request, obj)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('bid_number', 'name')
    search_fields = ['bid_number', 'name']
    list_filter = ['type']
#    readonly_fields = ['bid_number', 'name', 'max_winner' ] 
    list_display_links = ['bid_number', 'name']
    def get_actions(self, request):
        return []
    inlines = [TransactionInline]
    change_form_template = "auction/item_change_form.html"


class TransactionAdmin(admin.ModelAdmin):
    def customer(self):
        return "%s - %s" % (self.customer.paddle_number, self.customer.name)
    def item(self):
        return "%s - %s" % (self.item.bid_number, self.item.name)
    search_fields = ['customer__name', 'item__name']
    list_display = (customer, item, 'price')
    change_list_template = 'auction/transaction_change_list.html'
    list_filter = ['item__type']
    customer.admin_order_field= 'customer__paddle_number'
    item.admin_order_field= 'item__bid_number'
    list_per_page = 30

    def changelist_view(self, request, extra_context=None):
        r= super(TransactionAdmin, self).changelist_view(request, extra_context=extra_context)
        if hasattr(r, 'context_data'):
            c = r.context_data
            c['TransactionAmount'] = Transaction.objects.aggregate(Sum('price'))['price__sum']
            c['TransactionCount'] = Transaction.objects.aggregate(Count('id'))['id__count']
            c['CustomerCount'] = Customer.objects.aggregate(Count('id'))['id__count']
            c['CustomerPaidCount'] = Customer.objects.filter(paid=True).aggregate(Count('id'))['id__count']
            c['CustomerPaidAmount'] = Customer.objects.filter(paid=True).aggregate(Sum('paid_amount'))['paid_amount__sum']

            c['CustomerCashPaidAmount'] = Customer.objects.filter(paid=True, payment_method = 'CASH').aggregate(Sum('paid_amount'))['paid_amount__sum']
            c['CustomerCheckPaidAmount'] = Customer.objects.filter(paid=True, payment_method = 'CHECK').aggregate(Sum('paid_amount'))['paid_amount__sum']
            c['CustomerOtherPaidAmount'] = Customer.objects.filter(paid=True, payment_method = 'OTHER').aggregate(Sum('paid_amount'))['paid_amount__sum']
            c['CustomerCreditCardPaidAmount'] = Customer.objects.filter(paid=True,payment_method = 'CREDITCARD').aggregate(Sum('paid_amount'))['paid_amount__sum']
        return r   
        



admin.site.register(Item, ItemAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Transaction, TransactionAdmin)
