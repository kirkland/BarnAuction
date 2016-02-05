import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyweb.settings")

from auction.models import Customer, Item, Transaction

import time

import xlsxwriter

filename = 'barn_auction_transactions_2016.xlsx'
workbook = xlsxwriter.Workbook(filename)
worksheet = workbook.add_worksheet()

bold = workbook.add_format({'bold': True})
money = workbook.add_format({'num_format': '$#,##0'})

row = 0
col = 0

worksheet.write(row, col,     "Bidder Number", bold)
worksheet.write(row, col + 1, "Bidder Name", bold)
worksheet.write(row, col + 2, "Item Code", bold)  # (silent, live, raffle, etc.)
worksheet.write(row, col + 3, "Item #", bold)
worksheet.write(row, col + 4, "Item Name", bold)
worksheet.write(row, col + 5, "Amount", bold)
worksheet.write(row, col + 6, "Payment Method", bold)
row += 1

for t in Transaction.objects.all().order_by('item__bid_number'):
    worksheet.write(row, col,     t.customer.paddle_number)
    worksheet.write(row, col + 1, t.customer.name)
    worksheet.write(row, col + 2, t.item.type)
    worksheet.write(row, col + 3, t.item.bid_number)
    worksheet.write(row, col + 4, t.item.name)
    worksheet.write(row, col + 5, t.price, money)
    worksheet.write(row, col + 6, t.customer.payment_method)
    row += 1

# Write a total using a formula.
worksheet.write(row, 0, 'Total', bold)
worksheet.write(row, col + 5, '=SUM(F1:F{})'.format(row), money)

workbook.close()

print "Wrote {}".format(filename)

