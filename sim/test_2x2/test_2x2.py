"""

Copyright (c) 2020 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


import logging
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.regression import TestFactory

from cocotbext.axi import AxiBus, AxiMaster
from cocotbext.axi import AxiStreamBus, AxiStreamFrame, AxiStreamSource, AxiStreamSink

import random
import numpy as np
from functools  import reduce

def toByteList(x, length=4):
    val = x.item().to_bytes(length=length, byteorder='little', signed=True)
    return val

def axisFrame2np(frame):
    frame_btye = frame.tdata
    frame_btye_num = int(len(frame_btye)/2)
    np_data = np.frombuffer(frame_btye,count = frame_btye_num, dtype = np.int16)

    return np_data


def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list

class TB(object):
    def __init__(self, dut):
        self.dut = dut

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

        self.input_source = AxiStreamSource(AxiStreamBus.from_prefix(dut, "s_axis"), dut.clk, dut.rst)
        self.output_sink  = AxiStreamSink(AxiStreamBus.from_prefix(dut, "m_axis"), dut.clk, dut.rst)

    async def cycle_reset(self):
        self.dut.rst.setimmediatevalue(0)
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 1
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        await RisingEdge(self.dut.clk)


async def run_test_write(dut):

    tb = TB(dut)
    await tb.cycle_reset()

    ref_c_list = []
    test_num = 10
    for i in range(test_num):
        # a = np.array([0,4,1,-7],dtype=np.int8).reshape(2,2)
        # b = np.array([2,3,6,7],dtype=np.int8).reshape(2,2)
        a = np.array(random_int_list(-8,7,4),dtype=np.int8).reshape(2,2)
        b = np.array(random_int_list(-8,7,4),dtype=np.int8).reshape(2,2)

        c = np.dot(a,b).flatten()
        ref_c_list.append(c)
        data_np = np.hstack([a.T,b]).flatten()
        
        data_list = list(data_np)
        data_list = [toByteList(c, length=1) for c in data_list]
        data_bytes = reduce(lambda x,y:x+y,data_list)
        data_frame = AxiStreamFrame(data_bytes)
        await tb.input_source.send(data_frame)

    for i in range(1):
        pred_frame = await tb.output_sink.recv()
        # print(axisFrame2np(pred_frame))
        out1 = axisFrame2np(pred_frame)
        assert tb.output_sink.empty()

        pred_frame = await tb.output_sink.recv()
        # print(axisFrame2np(pred_frame))
        out2 = axisFrame2np(pred_frame)
        assert tb.output_sink.empty()

        out_hw = np.hstack([out2,out1])
        assert (out_hw == ref_c_list[i]).all()

    for i in range(600):
        await RisingEdge(dut.clk)

factory = TestFactory(run_test_write)
factory.generate_tests()



