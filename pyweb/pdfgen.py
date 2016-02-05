import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyweb.settings")

template_str = open('auction/templates/auction/bill.pdf.html', 'r').read()

from django.template import Template, Context
from django.db.models import Count, Min, Sum, Avg
from auction.models import Customer, Item, Transaction

template = Template(template_str)

def get_context(c):
    transactions = c.transaction_set.all()
    if transactions:
        transaction_sum = c.transaction_set.aggregate(Sum('price'))['price__sum']
    else:
        transaction_sum = 0
    if not c.paid_amount:
        c.paid_amount = 0
    formatted_transaction = [ '{:.<47}{:.>10}'.format(t.item.name,'${:.2f}'.format(t.price)) for t in transactions ]  

    formatted_sum = '{:.<47}{:.>10}'.format('Total','${:.2f}'.format(transaction_sum))
    formatted_paid = '{:.<47}{:.>10}'.format('Paid','${:.2f}'.format(c.paid_amount))
    balance = transaction_sum - c.paid_amount
    formatted_balance = '{:.<47}{:.>10}'.format('Balance','${:.2f}'.format(balance))
    formatted_extra = '{:.<47}{:.>10}'.format('Extra Donation','${:.2f}'.format(-1 * balance))
    return Context( {'customer' : c, 
                     'transactions' : formatted_transaction, 
                     'raw_sum' : transaction_sum,
                     'sum' : formatted_sum, 
                     'balance' : formatted_balance, 
                     'paid' : formatted_paid, 
                     'balance_num' : balance, 
                     'extra': formatted_extra,
                     'when_datetime' : c.modified_time })

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
##me = 'Acton Barn<li.changgeng@gmail.com>';
me = 'Acton Barn<brad.wasson@gmail.com>';

def send_email(me, to, file):
    msg = MIMEMultipart()
    msg['Subject'] = 'Your receipt for Spring 2016 Auction'
    msg['From'] = me
    msg['To'] = to
    msg.preamble = 'Your receipt for Sprint 2016 Auction'
    fp = open(file, 'rb')
    pdf = MIMEBase('application', 'pdf')
    pdf.add_header('Content-Disposition', 'attachment', filename=file)
    pdf.set_payload(fp.read())
    encoders.encode_base64(pdf)
    fp.close()
    msg.attach(pdf)
#    print msg.as_string()

    smtp = smtplib.SMTP('smtp.gmail.com:587')
    smtp.starttls()
    smtp.login('rob.m.kaufman@gmail.com','XXX-put-password-here')
    smtp.sendmail(me, to, msg.as_string())
    smtp.quit()
    print "Sent email to ", to, " Successfully"

import time
from fpdf import FPDF, HTMLMixin

class MyFPDF(FPDF, HTMLMixin):
    pass

skip_list = []
#yes_list = [8, 26, 61, 63]
yes_list = []

for c in Customer.objects.all():
    print "start of loop"
    print c
    if not c.email:
        print "no email"
        continue
    if not c.paid:
        print "not paid"
        continue
    if c.paid_amount is None:
        print "paid amount is none"
        continue
    if c.paddle_number in skip_list:
        continue

#    if c.paddle_number not in yes_list:
#        continue

    print "we made it yogi"

    context = get_context(c)

#    if float(c.paid_amount) != float(context['raw_sum']):
#        print "##############"

    print "Sending email to {} ({}) - paid amount ${} - transaction sum ${}".format(c.name, c.paddle_number, c.paid_amount, context['raw_sum'])
    html = template.render(context)
    #print html
    pdf=MyFPDF()
    pdf.add_page()
    pdf.write_html(html)
    pdf.output('receipt-%d.pdf' % (c.paddle_number),'F')

    send_email(me, c.email, 'receipt-%d.pdf' % (c.paddle_number))
    time.sleep(40)
