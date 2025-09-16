# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_project_compiles_and_runs(dut):
    """
    This is a minimal test that only checks if the design compiles
    and the simulation can be started and reset.
    """
    dut._log.info("Start minimal compilation test")

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # --- Manual Reset and Enable ---
    dut._log.info("Resetting DUT...")
    dut.rst_n.value = 0
    dut.ena.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut.ena.value = 1
    await ClockCycles(dut.clk, 10)
    dut._log.info("Reset done")

    dut._log.info("Design successfully compiled and reset. Test passed.")
    assert True
