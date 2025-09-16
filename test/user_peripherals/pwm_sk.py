# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer

# This helper class is part of the Tiny Tapeout test infrastructure
from tqv import TinyQV 

# FIX: Initialize with the peripheral *number*, not its memory address.
# Your module is simple peripheral #4. The test framework uses the
# convention of 16 + index for simple peripherals.
PERIPHERAL_NUM = 16 + 4

async def measure_pwm(dut, expected_duty_value):
    """
    Measures the PWM signal on io_out[8] to verify its duty cycle.
    """
    pwm_period = 256
    high_cycles = 0
    
    # Get a reference to the corrected PWM output pin
    pwm_pin = dut.io_out[8]

    # Handle the 0% duty cycle case (always low)
    if expected_duty_value == 0:
        await ClockCycles(dut.clk, pwm_period)
        assert pwm_pin.value == 0, f"FAIL: PWM should be constantly LOW for 0% duty, but was {pwm_pin.value}"
        return 0

    # Handle the 100% duty cycle case (always high in your Verilog)
    if expected_duty_value == 255:
        await ClockCycles(dut.clk, pwm_period)
        assert pwm_pin.value == 1, f"FAIL: PWM should be constantly HIGH for 100% duty, but was {pwm_pin.value}"
        return pwm_period

    # For other values, wait for a rising edge to start the measurement
    try:
        # The simulation clock is 100MHz (10ns period). Timeout after 2 PWM periods.
        await RisingEdge(pwm_pin, timeout=Timer(pwm_period * 2 * 10, units='ns'))
    except cocotb.result.SimTimeoutError:
        assert False, f"FAIL: Timed out waiting for rising edge. PWM for duty={expected_duty_value} is not toggling."

    # Count the number of high cycles over one full period
    for _ in range(pwm_period):
        if pwm_pin.value == 1:
            high_cycles += 1
        await ClockCycles(dut.clk, 1)
        
    return high_cycles


@cocotb.test()
async def test_pwm_duty_cycles(dut):
    dut._log.info("Start Comprehensive PWM Test")

    # The simulation runs at 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # FIX: Initialize the tqv helper with the peripheral NUMBER.
    tqv = TinyQV(dut, PERIPHERAL_NUM)

    await tqv.reset()
    dut._log.info("Reset done")

    # Define test cases: (duty_to_write, expected_high_cycles)
    test_cases = [
        (64, 64),      # 25% duty
        (192, 192),    # 75% duty
        (0, 0),        # 0% duty
        (255, 256),    # 100% duty
    ]

    for duty_value, expected_high in test_cases:
        dut._log.info(f"--- Testing Duty Cycle: {duty_value} ---")
        
        # Write the duty cycle value to register 0 of the peripheral
        await tqv.write_reg(0, duty_value)
        
        # Read back from the data_out port (io_out[7:0]) to verify the write
        readback_bus = await tqv.read_reg(0)
        readback_val = int(readback_bus & 0xFF)
        assert readback_val == duty_value, f"FAIL: Write failed! Expected {duty_value}, got {readback_val}"
        dut._log.info(f"Wrote duty={duty_value} and verified readback.")
        
        # Give the PWM a moment to stabilize
        await ClockCycles(dut.clk, pwm_period * 2)
        
        # Measure the actual duty cycle from the output pin
        measured_high = await measure_pwm(dut, duty_value)
        
        assert measured_high == expected_high, f"FAIL: Duty cycle mismatch! For duty={duty_value}, expected {expected_high} high cycles, but measured {measured_high}"
        dut._log.info(f"PASS: Verified {measured_high} high cycles as expected.")

    dut._log.info("All PWM test cases passed!")
