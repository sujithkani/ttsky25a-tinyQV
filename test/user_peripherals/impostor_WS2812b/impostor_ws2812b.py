import random
from cocotb.triggers import Timer

class WS2812BGenerator:
    def __init__(self, clk, din_signal):
        self.clk = clk
        self.din = din_signal
        self.bit_queue = []
        self.active = False

    def send_byte(self, byte):
        """Queue 8 bits MSB-first."""
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            self.bit_queue.append(bit)
        self.active = True

    def inject_idle(self, microseconds=60):
        """Add idle delay to simulate reset."""
        self.bit_queue.append(('IDLE', microseconds))
        self.active = True

    async def update(self):
        """Send one bit (or idle) per call."""
        if not self.bit_queue:
            self.active = False
            return

        bit = self.bit_queue.pop(0)
        if isinstance(bit, tuple) and bit[0] == 'IDLE':
            self.din.value = 0
            await Timer(bit[1] * 1000, units='ns')
            return

        # WS2812B timings
        if bit == 1:
            high_time = 800
            low_time  = 450
        else:
            high_time = 400
            low_time  = 850

        self.din.value = 1
        await Timer(high_time, units='ns')
        self.din.value = 0
        await Timer(low_time, units='ns')
