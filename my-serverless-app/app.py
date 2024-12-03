#!/usr/bin/env python3
import os

import aws_cdk as cdk

from my_serverless_app.my_serverless_app_stack import MyServerlessAppStack


app = cdk.App()
MyServerlessAppStack(app, "MyServerlessAppStack")

app.synth()
