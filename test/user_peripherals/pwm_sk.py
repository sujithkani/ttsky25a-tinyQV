# --- TEMPORARY DIAGNOSTIC SCRIPT ---
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer

@cocotb.test()
async def find_the_correct_path(dut):
    """
    This is a temporary test to discover the correct hierarchy path.
    The 'dut' object is a handle to the top-level module 'tb'.
    This test will print everything that is directly inside 'tb'.
    """
    
    dut._log.info("--- Starting Hierarchy Discovery Test ---")
    
    # We don't need a clock for this, just a small delay.
    await Timer(1, units='ns') 

    dut._log.info(f"Looking inside the top-level module named: '{dut._name}'")
    dut._log.info("-------------------------------------------")
    
    count = 0
    # This loop prints the name of every module instance inside 'tb'
    for obj in dut:
        dut._log.info(f" ---> Found object: {obj._name}")
        count += 1

    if count == 0:
        dut._log.info("Could not find any objects inside the top level.")
    
    dut._log.info("-------------------------------------------")
    dut._log.info("--- End of Hierarchy Discovery ---")
    dut._log.info("Please copy the log output from this run and send it back.")
    
    # This assertion will intentionally fail so the workflow stops and shows us the log.
    assert False, "This is a diagnostic test. See the log for hierarchy info."
