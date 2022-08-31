#!/usr/bin/python3
import pandas as pd
import printful

orders = printful.csv_orders()
for order in [orders[355], orders[361]]:
    order.send()
    order.confirm()
