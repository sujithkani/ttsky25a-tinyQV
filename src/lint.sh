#!/bin/bash

verilator --lint-only --timing -DSIM -Wall -Wno-DECLFILENAME -Wno-MULTITOP project.v tinyQV/cpu/*.v tinyQV/peri/*/*.v
