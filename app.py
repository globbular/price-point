#!/usr/bin/env python3

from aws_cdk import core

from price_point.price_point_stack import PricePointStack


app = core.App()
PricePointStack(app, "price-point", email='[Your email here]')

app.synth()
