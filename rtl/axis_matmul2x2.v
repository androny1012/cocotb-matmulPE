
module axis_matmul2x2(
    input                       clk             ,
    input                       rst             ,

    input                       s_axis_tvalid   ,
    input     [31 : 0]          s_axis_tdata    ,
    input                       s_axis_tlast    ,
    output                      s_axis_tready   ,

    output                      m_axis_tvalid   ,
    output    [31 : 0]          m_axis_tdata    ,
    output                      m_axis_tlast    ,
    input                       m_axis_tready   
);

    wire [3:0]  io_in_a_0;
    wire [3:0]  io_in_a_1;
    wire [3:0]  io_in_b_0;
    wire [3:0]  io_in_b_1;

    wire [15:0] io_out_c_0;
    wire [15:0] io_out_c_1;

    assign io_in_a_0 = s_axis_tdata[00+:4];
    assign io_in_a_1 = s_axis_tdata[08+:4];
    assign io_in_b_0 = s_axis_tdata[16+:4];
    assign io_in_b_1 = s_axis_tdata[24+:4];

    assign m_axis_tdata = {io_out_c_1,io_out_c_0};
    assign m_axis_tlast = m_axis_tvalid;
    
    top u_top(
        .clock        (clk              ),
        .reset        (rst              ),
        .io_in_valid  (s_axis_tvalid    ),
        .io_out_ready (s_axis_tready    ),
        .io_in_a_0    (io_in_a_0        ),
        .io_in_a_1    (io_in_a_1        ),
        .io_in_b_0    (io_in_b_0        ),
        .io_in_b_1    (io_in_b_1        ),
        .io_in_c_0    (16'b0            ),
        .io_in_c_1    (16'b0            ),
        .io_out_valid (m_axis_tvalid    ),
        .io_in_ready  (m_axis_tready    ),
        .io_out_c_0   (io_out_c_0       ),
        .io_out_c_1   (io_out_c_1       )
    );

endmodule