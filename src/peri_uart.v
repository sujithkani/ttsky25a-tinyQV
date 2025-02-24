/*
 * Copyright (c) 2025 Michael Bell
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// Simple UART TX wrapper
module tqvp_uart_tx (
    input         clk,
    input         rst_n,

    input  [7:0]  ui_in,        // The input PMOD, always available
    output [7:0]  uo_out,       // The output PMOD.  Each wire is only connected if this peripheral is selected

    input [5:0]   address,      // Address within this peripheral's address space
    input [31:0]  data_in,      // Data in to the peripheral, bottom 8, 16 or all 32 bits are valid on write.

    // Data read and write requests from the TinyQV core.
    input [1:0]   data_write_n, // 11 = no write, 00 = 8-bits, 01 = 16-bits, 10 = 32-bits
    input [1:0]   data_read_n,  // 11 = no read,  00 = 8-bits, 01 = 16-bits, 10 = 32-bits
    
    output [31:0] data_out,     // Data out from the peripheral, bottom 8, 16 or all 32 bits are valid on read when data_ready is high.
    output        data_ready,

    output        user_interrupt  // Each user peripheral gets an interrupt?  There may be a limit to how many we can easily support.
);

    wire uart_tx_busy;

    uart_tx #(.CLK_HZ(64_000_000), .BIT_RATE(115_200)) i_uart_tx(
        .clk(clk),
        .resetn(rst_n),
        .uart_txd(uo_out[0]),
        .uart_tx_en(data_write_n != 2'b11),
        .uart_tx_data(data_in[7:0]),
        .uart_tx_busy(uart_tx_busy) 
    );

    // Interrupt on ability to send
    assign user_interrupt = !uart_tx_busy;
    assign data_out = address == 6'h4 ? {31'b0, uart_tx_busy} : 32'd0;
    assign data_ready = 1;
    assign uo_out[7:1] = 0;

    wire _unused = &{data_read_n, data_in[31:8], ui_in, 1'b0};

endmodule

// Simple UART RX wrapper
module tqvp_uart_rx (
    input         clk,
    input         rst_n,

    input  [7:0]  ui_in,        // The input PMOD, always available
    output [7:0]  uo_out,       // The output PMOD.  Each wire is only connected if this peripheral is selected

    input [5:0]   address,      // Address within this peripheral's address space
    input [31:0]  data_in,      // Data in to the peripheral, bottom 8, 16 or all 32 bits are valid on write.

    // Data read and write requests from the TinyQV core.
    input [1:0]   data_write_n, // 11 = no write, 00 = 8-bits, 01 = 16-bits, 10 = 32-bits
    input [1:0]   data_read_n,  // 11 = no read,  00 = 8-bits, 01 = 16-bits, 10 = 32-bits
    
    output [31:0] data_out,     // Data out from the peripheral, bottom 8, 16 or all 32 bits are valid on read when data_ready is high.
    output        data_ready,

    output        user_interrupt  // Each user peripheral gets an interrupt?  There may be a limit to how many we can easily support.
);

    wire uart_rx_valid;
    wire [7:0] uart_rx_data;

    uart_rx #(.CLK_HZ(64_000_000), .BIT_RATE(115_200)) i_uart_rx(
        .clk(clk),
        .resetn(rst_n),
        .uart_rxd(ui_in[7]),
        .uart_rts(uo_out[1]),
        .uart_rx_read(data_read_n != 2'b11),
        .uart_rx_valid(uart_rx_valid),
        .uart_rx_data(uart_rx_data) 
    );

    // Interrupt on ability to send
    assign user_interrupt = uart_rx_valid;
    assign data_out = address == 6'h0 ? {24'd0, uart_rx_data} :
                      address == 6'h4 ? {31'd0, uart_rx_valid} :
                      32'd0;
    assign data_ready = 1;
    assign uo_out[7:2] = 0;
    assign uo_out[0] = 0;

    wire _unused = &{data_write_n, data_in, ui_in[6:0], 1'b0};

endmodule
