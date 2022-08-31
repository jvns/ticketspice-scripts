from requests.auth import HTTPBasicAuth
import requests
import json
import pandas as pd
import zoho

user, pw = "SECRET", "SECRET"
auth = HTTPBasicAuth(user, pw)


def get_products():
    return json.loads(
        requests.get("https://api.printful.com/store/products", auth=auth).text
    )["result"]


def csv_orders():
    orders = pd.read_csv("./orders.csv").to_dict("records")
    return [Order(x) for x in orders]


def get_orders():
    offset = 0
    all_results = []
    while True:
        results = json.loads(
            requests.get(
                "https://api.printful.com/orders?limit=100&offset=%d" % offset,
                auth=auth,
            ).text
        )["result"]
        if len(results) == 0:
            break
        all_results += results
        offset += 100
    return all_results


def get_variants(product_id):
    result = json.loads(
        requests.get(
            "https://api.printful.com/store/products/" + str(product_id), auth=auth
        ).text
    )
    return result["result"]["sync_variants"]


def get_variant_ids():
    variant_ids = {}
    products = get_products()
    for product in products:
        variants = get_variants(product["id"])
        for variant in variants:
            variant_ids[variant["name"]] = variant["id"]
    return variant_ids


mapping = {
    "address1": "Address (fill in so we can mail you a tshirt!) (Street Address)",
    "address2": "Address (fill in so we can mail you a tshirt!) (Street Address 2)",
    "city": "Address (fill in so we can mail you a tshirt!) (City)",
    "state_code": "Address (fill in so we can mail you a tshirt!) (State)",
    "zip": "Address (fill in so we can mail you a tshirt!) (ZIP/Postal Code)",
    "country_code": "Address (fill in so we can mail you a tshirt!) (Country)",
}

shirt_mapping = {
    "Unisex XS": "Short sleeve t-shirt - XS",
    "Unisex S": "Short sleeve t-shirt - S",
    "Unisex M": "Short sleeve t-shirt - M",
    "Unisex L": "Short sleeve t-shirt - L",
    "Unisex XL": "Short sleeve t-shirt - XL",
    "Unisex 2XL": "Short sleeve t-shirt - 2XL",
    "Unisex 3XL": "Short sleeve t-shirt - 3XL",
    "Fitted S": "Fitted shirt - S",
    "Fitted M": "Fitted shirt - M",
    "Fitted L": "Fitted shirt - L",
    "Fitted XL": "Fitted shirt - XL",
    "Fitted 2XL": "Fitted shirt - 2XL",
    "Sweater S": "Unisex Sweatshirt - S",
    "Sweater M": "Unisex Sweatshirt - M",
    "Sweater L": "Unisex Sweatshirt - L",
    "Sweater XL": "Unisex Sweatshirt - XL",
    "Sweater 2XL": "Unisex Sweatshirt - 2XL",
    "Sweater 3XL": "Unisex Sweatshirt - 3XL",
    "Sweater 4XL": "Unisex Sweatshirt - 4XL",
    "Sweater 5XL": "Unisex Sweatshirt - 5XL",
}


class Order(object):
    def __init__(self, order):
        self.order = order
        self.variant_ids = None

    def email(self):
        return self.order["Billing Email Address"]

    def address(self):
        return self.order[
            "Address (fill in so we can mail you a tshirt!) (Street Address)"
        ]

    def billing_address(self):
        return self.order["Billing Address (Address 1)"]

    def billing_address2(self):
        return self.order["Billing Address (Address 2)"]

    def billing_address_state(self):
        return self.order["Billing Address (State)"]

    def address_state(self):
        return self.order["Address (fill in so we can mail you a tshirt!) (State)"]

    def id(self):
        return str(self.order["Order ID"])

    def first_name(self):
        return self.order["Billing Name (First Name)"]

    def last_name(self):
        return self.order["Billing Name (Last Name)"]

    def shirt_size(self):
        return self.order["T-shirt size"]

    def recipient(self):
        recipient = {}
        for key in mapping.keys():
            if mapping[key] in self.order and not pd.isnull(self.order[mapping[key]]):
                recipient[key] = self.order[mapping[key]]
        recipient["name"] = self.first_name() + " " + self.last_name()
        return recipient

    def email_shipping_confirmation(self):
        body = self.format_email()
        if body is None:
            print("Nothing shipped yet")
            return
        to = self.email()
        subject = "Your !!Con tshirt has shipped!"
        zoho.send_mail(to, subject, body)

    def send(self):
        if self.variant_ids is None:
            self.variant_ids = get_variant_ids()
        recipient = self.recipient()
        if pd.isnull(self.shirt_size()):
            print("No shirt size chosen")
            return
        variant_id = self.variant_ids[shirt_mapping[self.shirt_size()]]
        request = {
            "recipient": recipient,
            "external_id": self.id(),
            "items": [
                {
                    "sync_variant_id": variant_id,
                    "quantity": 1,
                }
            ],
        }
        result = json.loads(
            requests.post(
                "https://api.printful.com/orders", auth=auth, json=request
            ).text
        )
        if result["code"] != 200:
            if result["result"] == "Order with this External ID already exists":
                print("Already done.")
            else:
                print(result)
        else:
            print("Success!")

    def confirm(self):
        url = "https://api.printful.com/orders/@{order}/confirm".format(order=self.id())
        result = json.loads(requests.post(url, auth=auth).text)
        if result["code"] != 200:
            print(json.dumps(result))
        else:
            print("Success!")

    def get(self):
        return json.loads(
            requests.get(
                "https://api.printful.com/orders/@" + self.id(), auth=auth
            ).text
        )

    def format_email(self):
        try:
            shipments = self.get()["result"]["shipments"]
        except:
            return None
        if len(shipments) == 0:
            return None
        shipment = shipments[0]
        return """Hi {first}!

Our tshirt provider told us that your !!Con shirt (or sweater) just got shipped!
Here's the information they gave us:

Carrier: {carrier}
Tracking number: {tracking_number}
Tracking URL: {tracking_url}
Packing slip: {packing_slip_url}

Sometimes the tracking number takes a while to get activated in the system, so the link might not work right away.
If you run into problems let us know and we can try to figure out what happened with Printful!
""".format(
            first=self.first_name(),
            carrier=shipment["carrier"],
            tracking_number=shipment["tracking_number"],
            tracking_url=shipment["tracking_url"],
            packing_slip_url=shipment["packing_slip_url"],
        )


def search_orders(orders, text):
    return dict((i, x) for i, x in enumerate(orders) if text in str(x))


if __name__ == "__main__":
    variant_ids = get_variant_ids()
