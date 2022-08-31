#!/usr/bin/python3
import pandas as pd
import printful


def check_reason(num, order):
    if num < 10:
        pass
        # print(num, "Reason: num < 10")
    elif order.email() in []:  # manual
        # emailed them, they said they didn't want one
        pass
    elif order.email() in []:  # manual
        # replied to email saying they want one
        print(num, "they emailed us, go fix it!", order.email())
    elif pd.isnull(order.address()) and pd.isnull(order.shirt_size()):
        pass
        # print(num, "didn't want a shirt I guess? (%s %s)" % (order['Billing Name (First Name)'], order['Billing Name (Last Name)']))
    elif pd.isnull(order.address()):
        print(num, "No address but there's a shirt size??", order.email())
    elif pd.isnull(order.shirt_size()):
        print(num, "Missing shirt size", order.email())
    elif pd.isnull(order.address_state()):
        print(num, "Missing state", order.email())
    else:
        print(num, "No reason found!!", order.email())


orders = printful.csv_orders()
all_orders = printful.get_orders()
order_ids = set(x["external_id"] for x in all_orders)
missing_orders = [(i, x) for i, x in enumerate(orders) if x.id() not in order_ids]

for num, order in missing_orders:
    check_reason(num, order)
