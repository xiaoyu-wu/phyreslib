# FIXME: Refactor using official NI package nidaqmx?

# Major library imports
import numpy
from PyDAQmx import (
    Task, int32, byref, DAQmx_Val_Cfg_Default, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps,
    DAQmx_Val_Volts, DAQmx_Val_RisingSlope, DAQmx_Val_GroupByChannel
)

# Enthought library imports
from traits.api import HasTraits


class NI6259(HasTraits):
    def __init__(self, DeviceName, *args, **kwargs):
        super(NI6259, self).__init__(*args, **kwargs)
        self.DeviceName = DeviceName

    def sync_aoai(self, ao_ch_num, ai_ch_num, ao_data, time, ao_sample_rate, ai_sample_rate):
        if len(ao_data) != time * ao_sample_rate:
            raise RuntimeError("Output sequence does not match with number of output samples.")
            return

        ao = Task()
        ai = Task()
        read = int32()
        write = int32()

        ai_data = numpy.zeros(int(time * ai_sample_rate), dtype=numpy.float64)
        t_data = numpy.zeros(int(time * ai_sample_rate), dtype=numpy.float64)
        for i in range( int(time * ai_sample_rate) ):
            t_data[i] = float(i) / (time * ai_sample_rate) * time

        # DAQmx Configure Code

        ai.CreateAIVoltageChan(self.DeviceName+"/ai"+str(ai_ch_num),"",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
        ai.CfgSampClkTiming("", ai_sample_rate, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, int(time*ai_sample_rate))

        ao.CreateAOVoltageChan(self.DeviceName+"/ao"+str(ao_ch_num),"",-10.0,10.0,DAQmx_Val_Volts,None)
        ao.CfgSampClkTiming("", ao_sample_rate, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, int(time*ao_sample_rate))

        ao.CfgDigEdgeStartTrig("/"+self.DeviceName+"/ai/StartTrigger", DAQmx_Val_RisingSlope)

        # DAQmx Write Code
        ao.WriteAnalogF64(int(time*ao_sample_rate), 0, 10.0, DAQmx_Val_GroupByChannel, ao_data, byref(write), None)
        #print "Samples written:", write.value

        # DAQmx Start Code
        ao.StartTask()
        ai.StartTask()

        # DAQmx Read Code
        ai.ReadAnalogF64(int(time*ai_sample_rate), 10.0, DAQmx_Val_GroupByChannel, ai_data, int(time*ai_sample_rate), byref(read), None)
        #print "Samples read:", read.value

        # DAQmx Clear Code
        ao.ClearTask()
        ai.ClearTask()

        return [t_data, ai_data]

    def averaged_ai(self, AIchannel, num_samps):
        data = numpy.zeros(num_samps, dtype = numpy.float64)

        ai = Task()
        aipath = self.DeviceName + "/" + AIchannel
        ai.CreateAIVoltageChan(aipath,"",DAQmx_Val_Cfg_Default, -10, 10, DAQmx_Val_Volts, None)
        ai.CfgSampClkTiming("",1000,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps, num_samps)

        ai.StartTask()
        ai.ReadAnalogF64(num_samps,10.0,DAQmx_Val_GroupByChannel,data,num_samps,None,None)

        ai.StopTask()
        ai.ClearTask()

        average = sum(data)/num_samps
        return average

    def set_ao(self, ao_channel, value):
        ao = Task()
        aopath = self.DeviceName + "/ao" + str(ao_channel)
        ao.CreateAOVoltageChan(aopath, "", -10.0, 10.0, DAQmx_Val_Volts, None)
        ao.StartTask()
        ao.WriteAnalogScalarF64(1, 10.0, value, None)
        ao.StopTask()

def averageArray(input_array, averaging_points):
    if type(input_array) != numpy.ndarray:
        print "Input array must be numpy array type!"
    else:
        input_array_length = input_array.size
        output_array_length = input_array_length // averaging_points
        output_array = numpy.zeros(output_array_length, dtype=numpy.float64)
        for j in range(output_array_length):
            output_array[j] = numpy.average(input_array[averaging_points*j:averaging_points*(j+1):1])
        return output_array


if __name__ == "__main__":
    ni6259 = NI6259('NI6259')
