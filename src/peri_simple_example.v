/*
 * Copyright (c) 2025 Michael Bell
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// Peripheral template for a simple TinyQV peripheral
module tqvp_simple_example (
    input         clk,
    input         rst_n,

    input  [7:0]  ui_in,        // The input PMOD, always available
    output [7:0]  uo_out,       // The output PMOD.  Each wire is only connected if this peripheral is selected

    input [3:0]   address,      // Address within this peripheral's address space

    input         data_write,   // Data write request from the TinyQV core.
    input [7:0]   data_in,      // Data in to the peripheral, valid when data_write is high.
    
    output [7:0]  data_out      // Data out from the peripheral, set this in accordance with the supplied address
);

    // Implement an 8-bit read/write register at address 0
    reg [7:0] example_data;
    always @(posedge clk) begin
        if (!rst_n) begin
            example_data <= 0;
        end else begin
            if (address == 4'h0) begin
                if (data_write) example_data <= data_in;
            end
        end
    end

    // The stored data is output to uo_out.
    assign uo_out = example_data;

    // Address 0 reads the example data register.  
    // Address 1 reads ui_in
    // All other addresses read 0.
    assign data_out = (address == 4'h0) ? example_data :
                      (address == 4'h1) ? ui_in :
                      8'h0;
endmodule
