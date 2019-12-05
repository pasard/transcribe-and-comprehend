#!/usr/bin/env python3

from aws_cdk import core

from stacks.tc_stack import TCStack

app = core.App()
TCStack(app, "tc-stack")

app.synth()
