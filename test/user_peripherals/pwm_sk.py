import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_pwm_simple_pass(dut):
    dut._log.info("Start simple passing test")

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # --- Step 1: Manual Reset and Enable ---
    dut._log.info("Resetting DUT...")
    dut.rst_n.value = 0
    dut.ena.value = 0
    dut.ui_in.value = 0 # This controls io_in[7:0]
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut.ena.value = 1
    await ClockCycles(dut.clk, 10)
    dut._log.info("Reset done")

    # --- Step 2: Write a duty cycle using the remapped low-order pins ---
    # We remapped data_write to io_in[0] and data_in[7:1] to io_in[7:1]
    
    # Set data bits for duty cycle = 64 (0100 0000) on pins 7:1
    # and assert write on pin 0
    write_value = (64 << 1) | 1 
    dut.ui_in.value = write_value
    
    await ClockCycles(dut.clk, 1)
    
    # De-assert write
    dut.ui_in.value = (64 << 1) | 0
    dut._log.info("Sent duty cycle = 64 to remapped pins.")

    # --- Step 3: Check for PWM output toggle ---
    pwm_pin = dut.user_project.io_out[8]
    
    dut._log.info("Waiting for PWM signal to toggle...")
    await ClockCycles(dut.clk, 300) # Wait for PWM to start
    
    initial_value = pwm_pin.value
    
    toggled = False
    for i in range(256):
        if pwm_pin.value != initial_value:
            toggled = True
            dut._log.info(f"SUCCESS: PWM toggled at cycle {i+300}")
            break
        await ClockCycles(dut.clk, 1)

    assert toggled, "FAIL: PWM signal did not toggle."
    dut._log.info("Test passed: PWM is active.")
