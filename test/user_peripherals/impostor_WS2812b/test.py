# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from impostorWS2812b import WS2812BGenerator
from tqv import TinyQV

PERIPHERAL_NUM = 18
REGISTER_DELAY = 100

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start WS2812B simulation test")

    # Set a 64 MHz clock (approx 15.625 ns)
    clock = Clock(dut.clk, 16, units="ns")
    cocotb.start_soon(clock.start())

    generator = WS2812BGenerator(dut.clk, dut.ui_in[1])

    tqv = TinyQV(dut, PERIPHERAL_NUM)
    await tqv.reset()

    # Check ready flag is 0
    dut._log.info("Checking initial rgb_ready state")
    assert await tqv.read_reg(15) == 0

    # Send G=0x12, R=0x34, B=0x56
    dut._log.info("Sending RGB values")
    generator.send_byte(0x12)
    generator.send_byte(0x34)
    generator.send_byte(0x56)

    while generator.active:
        await generator.update()

    await ClockCycles(dut.clk, REGISTER_DELAY)

    # Check that data latched
    assert await tqv.read_reg(15) == 0xFF
    await tqv.write_reg(14, 0)
    await ClockCycles(dut.clk, 1)
    assert await tqv.read_reg(15) == 0x00

    g = await tqv.read_reg(1)
    r = await tqv.read_reg(0)
    b = await tqv.read_reg(2)

    dut._log.info(f"Received RGB = ({r:02X}, {g:02X}, {b:02X})")
    assert r == 0x34
    assert g == 0x12
    assert b == 0x56

    # Send another set of bytes
    dut._log.info("Sending another RGB (DE, AD, FF)")
    generator.send_byte(0xDE)
    generator.send_byte(0xAD)
    generator.send_byte(0xFF)

    while generator.active:
        await generator.update()
    await ClockCycles(dut.clk, REGISTER_DELAY)

    assert await tqv.read_reg(15) == 0xFF
    await tqv.write_reg(14, 0)
    await ClockCycles(dut.clk, 1)
    assert await tqv.read_reg(15) == 0x00

    # Inject idle to simulate reset
    dut._log.info("Injecting idle line > 50us")
    generator.inject_idle()
    while generator.active:
        await generator.update()

    await ClockCycles(dut.clk, REGISTER_DELAY)

    # Send new RGB
    dut._log.info("Sending RGB after idle (AB, CD, EF)")
    generator.send_byte(0xAB)
    generator.send_byte(0xCD)
    generator.send_byte(0xEF)

    while generator.active:
        await generator.update()

    await ClockCycles(dut.clk, REGISTER_DELAY)

    g = await tqv.read_reg(1)
    r = await tqv.read_reg(0)
    b = await tqv.read_reg(2)

    dut._log.info(f"Post-idle RGB = ({r:02X}, {g:02X}, {b:02X})")
    assert r == 0xCD
    assert g == 0xAB
    assert b == 0xEF

    dut._log.info("WS2812B test complete")
