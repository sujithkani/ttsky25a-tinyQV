#!/bin/bash

verilator --lint-only --timing -DSIM -Wall -Wno-DECLFILENAME -Wno-MULTITOP project.v peri*.v tinyQV/cpu/*.v tinyQV/peri/*/*.v
