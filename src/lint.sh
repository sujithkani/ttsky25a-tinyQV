#!/bin/bash

verilator --lint-only -DSIM -Wall -Wno-DECLFILENAME -Wno-MULTITOP project.v tinyQV/cpu/*.v tinyQV/peri/*/*.v
