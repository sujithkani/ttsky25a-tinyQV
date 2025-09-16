# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
WAVES ?= 1
TOPLEVEL_LANG ?= verilog
PROG ?= hello
PROG_FILE ?= $(PROG).hex
SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = project.v peri*.v tinyQV/cpu/*.v tinyQV/peri/uart/uart_tx.v user_peripherals/*/*.v user_peripherals/*.v user_peripherals/*.sv user_peripherals/*/*.sv

VERILOG_SOURCES += sim_qspi.v
COMPILE_ARGS +=  -DPROG_FILE=\"$(PROG_FILE)\"

ifneq ($(GATES),yes)

ifneq ($(SYNTH),yes)

# RTL simulation:
SIM_BUILD				= sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS 		+= -DSIM
COMPILE_ARGS 		+= -DPURE_RTL
COMPILE_ARGS 		+= -I$(SRC_DIR)
COMPILE_ARGS 		+= -I$(addprefix $(SRC_DIR)/,user_peripherals/pwl_synth)

else

SIM_BUILD				= sim_build/synth
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

NL ?= placement

#VERILOG_SOURCES += ../runs/wokwi/results/synthesis/tt_um_tt_tinyQV.v
VERILOG_SOURCES += ../runs/wokwi/results/$(NL)/tt_um_tt_tinyQV.nl.v

endif

else

# Gate level simulation:
SIM_BUILD				= sim_build/gl
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# this gets copied in by the GDS action workflow
#VERILOG_SOURCES += ../runs/wokwi/results/placement/tt_um_tt_tinyQV.pnl.v
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb_qspi.v
TOPLEVEL = tb_qspi

# MODULE is the basename of the Python test file
MODULE = test_$(PROG)

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
