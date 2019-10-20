import boto3
import argparse
import time
from decimal import *

parser = argparse.ArgumentParser(description='Upload a product to watch on PricePoint')
parser.add_argument("url", help="the URL of the webpage where the product's price is",
                    type=str)
parser.add_argument("selector", help="the query selector of the DOM element which contains the price of the product",
                    type=str)
parser.add_argument("--attr", help="the attribute of the selected element to extract the price from e.g. 'data-price'. If attr is not supplied, PricePoint will simply take the text of the selected element",
                    type=str)                    
parser.add_argument("product_name", help="the name of the product to watch",
                    type=str)
parser.add_argument("currency", help="the symbol or name of the currency the product is in. PricePoint will use this to extract the price from the element",
                    type=str)                                    
parser.add_argument("price", help="the desired price. PricePoint will alert when the product is less than or equal to this price",
                    type=float)
parser.add_argument("dynamo_db_table_name", help="the name of the DynamoDB table created by the CDK stack",
                    type=str)
args = parser.parse_args()

# Get the service resource.
dynamodb = boto3.resource('dynamodb')
# Get the table
table = dynamodb.Table(args.dynamo_db_table_name)

response = {}
ts = int(time.time())

# Put item with selector -> attr
if args.attr:
    response = table.put_item(
    Item={
            'ProductTs': ts,
            'Url': args.url,
            'Selector': {
                "Value": args.selector,
                "Attr": args.attr
            },
            'ProductName': args.product_name,
            'Currency': args.currency,
            'Threshold': Decimal(str(args.price)),
            'PrevPrice': Decimal("-1.00")
        }
    )
else:
    response = table.put_item(
    Item={
            'ProductTs': ts,
            'Url': args.url,
            'Selector': {
                "Value": args.selector
            },
            'ProductName': args.product_name,
            'Currency': args.currency,
            'Threshold': Decimal(str(args.price)),
            'PrevPrice': Decimal("-1.00")
        }
    )
print(response)