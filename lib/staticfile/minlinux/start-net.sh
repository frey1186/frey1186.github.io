#!/bin/bash

brctl addif br0 tap0
ip l set br0 up
ip l set tap0 up
