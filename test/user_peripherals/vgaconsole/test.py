# SPDX-FileCopyrightText: © 2025 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock, Timer
from cocotb.triggers import Edge, ClockCycles, RisingEdge, FallingEdge
import numpy as np
import imageio.v2 as imageio
import random

from tqv import TinyQV

# When submitting your design, change this to the peripheral number
# in peripherals.v.  e.g. if your design is i_user_peri05, set this to 5.
# The peripheral number is not used by the test harness.
PERIPHERAL_NUM = 13

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # VGA signals
    hsync = dut.uo_out[7]
    vsync = dut.uo_out[3]
    R0 = dut.uo_out[4]
    G0 = dut.uo_out[5]
    B0 = dut.uo_out[6]
    R1 = dut.uo_out[0]
    G1 = dut.uo_out[1]
    B1 = dut.uo_out[2]

    # 64 MHz
    clock = Clock(dut.clk, 15626, units="ps")
    cocotb.start_soon(clock.start())

    # Interact with your design's registers through this TinyQV class.
    # This will allow the same test to be run when your design is integrated
    # with TinyQV - the implementation of this class will be replaces with a
    # different version that uses Risc-V instructions instead of the SPI test
    # harness interface to read and write the registers.
    tqv = TinyQV(dut, PERIPHERAL_NUM)

    # Reset
    await tqv.reset()

    dut._log.info("Test project behavior")

    # clear console (all spaces)
    for i in range(30):
        await tqv.write_word_reg(i, 32)

    await tqv.write_byte_reg(0x30, 0b010000)  # backgrond color = dark blue
    await tqv.write_byte_reg(0x31, 0b001100)  # text color 1 = green
    await tqv.write_byte_reg(0x32, 0b110011)  # text color 2 = magenta

    # write text using color 1
    for (i, ch) in enumerate("VGA"):
        await tqv.write_byte_reg(0+i, ord(ch))
    # write text using color 2
    for (i, ch) in enumerate("CONSOLE"):
        await tqv.write_byte_reg(10+i, 0x80 | ord(ch))
    # write text alternating colors
    for (i, ch) in enumerate("PERIPHERAL"):
        await tqv.write_byte_reg(20+i, ((i & 1) << 7) | ord(ch))

    # # grab next VGA frame and compare with reference image
    # vgaframe = await grab_vga(dut, hsync, vsync, R1, R0, B1, B0, G1, G0)
    # #imageio.imwrite("vga_grab1.png", vgaframe * 64)
    # vgaframe_ref = imageio.imread("vga_ref1.png") / 64
    # assert np.all(vgaframe == vgaframe_ref)

    # change colors
    await tqv.write_byte_reg(0x30, 0b000000)  # backgrond color = black
    await tqv.write_byte_reg(0x31, 0b111100)  # text color 1 = teal
    await tqv.write_byte_reg(0x32, 0b000011)  # text color 2 = red

    # write non-printable ASCII characters in top-right corner
    await tqv.write_byte_reg(8, 31)
    await tqv.write_byte_reg(9, 0x80 | 0)
    await tqv.write_byte_reg(10+9, 13)

    # grab next VGA frame and compare with reference image
    vgaframe = await grab_vga(dut, hsync, vsync, R1, R0, B1, B0, G1, G0)
    #imageio.imwrite("vga_grab2.png", vgaframe * 64)
    vgaframe_ref = imageio.imread("vga_ref2.png") / 64
    assert np.all(vgaframe == vgaframe_ref)

    # check interrupt behavior
    dut._log.info("Test interrupt behavior")

    for _ in range(2):  # skip past line 768
        while hsync.value.integer == 1:
            await Edge(dut.uo_out)
        while hsync.value.integer == 0:
            await Edge(dut.uo_out)

    assert await tqv.is_interrupt_asserted() == True
    vga_status = await tqv.read_byte_reg(0x3F)  # read VGA register to clear interrupt
    assert vga_status & 0x01 != 0
    assert await tqv.is_interrupt_asserted() == False
    vga_status = await tqv.read_byte_reg(0x3F)
    assert vga_status & 0x01 == 0


# Grab one VGA frame from the DUT.
# Returns a (height, width, 3) numpy array with 2-bit RGB values.
# Default: 1024x768 @ 60Hz timing with 22 line vertical back porch
# and 152 pixel horizontal back porch.
# NOTICE: it assumes that the pixel clock is the same as the system clock.
async def grab_vga(dut, hsync, vsync, R1, R0, B1, B0, G1, G0,
                   width=1024, height=768, v_back_porch_lines=28, h_back_porch_pixels=152):
    vga_frame = np.zeros((height, width, 3), dtype=np.uint8)

    # sync to the end of the vsync pulse
    dut._log.info("grab VGA frame: wait for vsync")
    while vsync.value.integer == 0:
        await Edge(dut.uo_out)
    while vsync.value.integer == 1:  # wait for vsync pulse to finish
        await Edge(dut.uo_out)
    dut._log.info("grab VGA frame: start")

    # if hsync is low, clear this pulse
    if hsync.value.integer == 0:
        while hsync.value.integer == 0:
            await Edge(dut.uo_out)

    # skip v_back_porch_lines
    for _ in range(v_back_porch_lines):
        while hsync.value.integer == 1:
            await Edge(dut.uo_out)
        while hsync.value.integer == 0:
            await Edge(dut.uo_out)

    # grab lines
    for ypos in range(height):
        # sync to end of hsync pulse
        while hsync.value.integer == 1:
            await Edge(dut.uo_out)
        while hsync.value.integer == 0:
            await Edge(dut.uo_out)

        # skip h_back_porch_pixels
        await ClockCycles(dut.clk, h_back_porch_pixels)

        # sync to falling edge of clk to sample mid-pixel
        await FallingEdge(dut.clk)

        # grab pixels
        for xpos in range(width):
            vga_frame[ypos][xpos][0] = (R1.value.integer << 1) | R0.value.integer
            vga_frame[ypos][xpos][1] = (G1.value.integer << 1) | G0.value.integer
            vga_frame[ypos][xpos][2] = (B1.value.integer << 1) | B0.value.integer

            # wait 1 clock cycle for next pixel
            await RisingEdge(dut.clk)
            await FallingEdge(dut.clk)

    dut._log.info("grab VGA frame: done")

    return vga_frame
