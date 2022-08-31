#!/usr/bin/python3
import pandas as pd
import printful

orders = printful.csv_orders()
print(orders[315].first_name(), orders[315].last_name())
import sys
sys.exit(0)
for i, order in enumerate(orders):
    if pd.isnull(order.address()):
        continue
    if pd.isnull(order.billing_address()):
        continue
    x = ''
    if not pd.isnull(order.billing_address2()):
        x = order.billing_address2()
    if order.address() != order.billing_address():
        print(i, order.address(), '|||', order.billing_address(), x)
