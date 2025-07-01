from cocotb.triggers import ClockCycles

from riscvmodel.insn import *
from riscvmodel.regnames import x0, tp, a0, a1

import test_util

class TinyQV:
    def __init__(self, dut, peripheral_num, base_address):
        self.dut = dut
        self.peripheral_num = peripheral_num
        self.base_address = base_address

    async def reset(self):
        await test_util.reset(self.dut)

        # Should start reading flash after 1 cycle
        await ClockCycles(self.dut.clk, 1)
        await test_util.start_read(self.dut, 0)
        
        await test_util.set_all_outputs_to_peripheral(self.dut, self.peripheral_num)

    async def write_reg(self, reg, value):
        await test_util.send_instr(self.dut, InstructionADDI(a0, tp, self.base_address).encode())
        await test_util.send_instr(self.dut, InstructionADDI(a1, x0, value).encode())
        await test_util.send_instr(self.dut, InstructionSB(a0, a1, reg).encode())


    async def read_reg(self, reg):
        await test_util.send_instr(self.dut, InstructionADDI(a0, tp, self.base_address).encode())
        await test_util.send_instr(self.dut, InstructionLBU(a1, a0, reg).encode())
        return await test_util.read_reg(self.dut, a1)