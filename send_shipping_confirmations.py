#!/usr/bin/python3
import printful
import zoho
import pandas as pd

orders = printful.csv_orders()
printful_orders = printful.get_orders()
printful_orders = dict((x['external_id'],x) for x in printful_orders)
for i, order in enumerate(orders):
    to = order.email()
    if order.id() not in printful_orders:
        continue
    shipments = printful_orders[order.id()]['shipments']
    if len(shipments) == 0:
        continue
    if zoho.already_sent(to):
        continue
    #print("would have sent: ", i, order.email())
    order.email_shipping_confirmation()
