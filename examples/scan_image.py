# Standard library imports
from threading import Thread
import time

# Major library imports
import numpy as np

# Enthought library imports
from traits.api import HasTraits, Instance, Button, on_trait_change
from traitsui.api import Item, View

from phyreslib.data_source.api import ImageDataSource, LineDataSource
from phyreslib.ui.api import ImagePlotUI, LinePlotUI
from phyreslib.measurement.api import ImageDataGenerator


# Use thread for measurement in case of stopping halfway
class ScanThread(Thread):
    def run(self):
        # Update data source
        self.image_data_source.xs = self.fast_axis_array
        self.image_data_source.ys = self.slow_axis_array
        self.image_data_source.zs = np.zeros((256,256))
        self.line_data_source.xs = self.fast_axis_array
        for i in range(256):
            if not self.wants_abort:
                now = time.time()
                # Update one line of the matrix zs
                self.image_data_source.zs[i] = self.image_data_generator.get_new_line()
                self.line_data_source.ys = self.image_data_source.zs[i]
                # Update value of image_data_source.last_update to trigger event, data_source_changed
                self.image_data_source.last_update = str(now)
                elapsed = time.time() - now
                remaining = self.scan_period - elapsed
                if remaining > 0:
                    time.sleep(remaining)
        return


class Demo(HasTraits):
    # components
    image_data_source = Instance(ImageDataSource)
    image_plot = Instance(ImagePlotUI)

    line_data_source = Instance(LineDataSource)
    line_plot = Instance(LinePlotUI)

    image_data_generator = Instance(ImageDataGenerator)
    scan_thread = Instance(ScanThread)
    btn_start_scan = Button("Start/Stop Scan")

    # button function
    def _btn_start_scan_fired(self):
        if self.scan_thread and self.scan_thread.isAlive():
            self.scan_thread.wants_abort = True
        else:
            self.scan_thread = ScanThread()
            self.scan_thread.wants_abort = False
            self.scan_thread.image_data_source = self.image_data_source
            self.scan_thread.line_data_source = self.line_data_source
            self.scan_thread.fast_axis_array = np.linspace(0, 5, 256)
            self.scan_thread.slow_axis_array = np.linspace(0, 5, 256)
            self.image_data_generator.reset_index()
            self.scan_thread.image_data_generator = self.image_data_generator
            self.scan_thread.scan_period = 0.1
            self.scan_thread.start()

    # Traits view
    traits_view = View(
        Item('image_plot', style='custom', show_label=False),
        Item('line_plot', style='custom', show_label=False),
        Item('btn_start_scan', style='custom', show_label=False),
        resizable=True
    )

    def __init__(self, *args, **kwargs):
        super(Demo, self).__init__(*args, **kwargs)
        self.image_plot = ImagePlotUI()
        self.image_data_source = ImageDataSource()
        self.line_plot = LinePlotUI()
        self.line_data_source = LineDataSource()
        self.image_data_generator = ImageDataGenerator()

    @on_trait_change('image_data_source, image_data_source.data_source_changed')
    def update_image_plot(self):
        self.image_plot.update(self.image_data_source)

    @on_trait_change('line_data_source, line_data_source.data_source_changed')
    def update_line_plot(self):
        self.line_plot.update(self.line_data_source)


def test():
    demo = Demo()
    demo.configure_traits()

if __name__ == '__main__':
    test()
