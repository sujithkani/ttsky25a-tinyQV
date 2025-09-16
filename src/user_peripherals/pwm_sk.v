/*
 * Copyright (c) 2025 Sujith Kani
 * SPDX-License-Identifier: Apache-2.0
 */
`default_nettype none
module tqvp_pwm_sujith(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] ui_in,
    input  wire [3:0] address,
    input  wire       data_write,
    input  wire [7:0] data_in,
    output wire       pwm_out,      // FIX: Clean, single-bit PWM output.
    output wire [6:0] counter_out,  // FIX: Separate output for the counter bits.
    output wire [7:0] data_out
);

    // --- INTERNAL LOGIC (Unchanged) ---
    reg [7:0] duty;
    reg [7:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            duty <= 8'd0;
        else if (data_write && address == 4'h0)
            duty <= data_in;
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            counter <= 8'd0;
        else
            counter <= counter + 1;
    end

    assign data_out = (address == 4'h0) ? duty : 8'd0;

    // --- OUTPUT ASSIGNMENTS (Corrected) ---

    // Assign the core PWM logic to its dedicated output port.
    assign pwm_out = (duty == 8'd0)   ? 1'b0 :
                     (duty == 8'd255) ? 1'b1 :
                     (counter < duty);

    // Assign the counter bits to their dedicated output port.
    assign counter_out = counter[7:1];
endmodule
