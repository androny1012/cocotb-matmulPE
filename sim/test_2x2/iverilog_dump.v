module iverilog_dump();
initial begin
    $dumpfile("axis_matmul2x2.fst");
    $dumpvars(0, axis_matmul2x2);
end
endmodule
