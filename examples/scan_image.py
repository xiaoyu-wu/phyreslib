# Standard library imports
from threading import Thread
import time

# Major library imports
import numpy as np

# Enthought library imports
from traits.api import HasTraits, Instance, Button, on_trait_change
from traitsui.api import Item, View

from ..data_source.api import ImageDataSource
from ..ui.api import ImagePlotUI
from ..measurement.api import ImageDataGenerator

# Use thread for measurement in case of stopping halfway
class ScanThread(Thread):
    def run(self):
        # Update data source
        self.image_data_source.xs = self.fast_axis_array
        self.image_data_source.ys = self.slow_axis_array
        self.image_data_source.zs = np.zeros((256,256))
        for i in range(256):
            if not self.wants_abort:
                now = time.time()
                # Update one line of the matrix zs
                self.image_data_source.zs[i] = self.image_data_generator.get_new_line()
                # Update value of image_data_source.last_update to trigger event, data_source_changed
                self.image_data_source.last_update = str(now)
                elapsed = time.time() - now
                remaining = self.scan_period - elapsed
                if remaining > 0:
                    time.sleep(remaining)
        return


class Demo(HasTraits):
    # components
    ds = Instance(ImageDataSource)
    ip1 = Instance(ImagePlotUI)
    idg = Instance(ImageDataGenerator)
    scan_thread = Instance(ScanThread)
    btnStartScan = Button("Start/Stop Scan")

    # button function
    def _btnStartScan_fired(self):
        if self.scan_thread and self.scan_thread.isAlive():
            self.scan_thread.wants_abort = True
        else:
            self.scan_thread = ScanThread()
            self.scan_thread.wants_abort = False
            self.scan_thread.image_data_source = self.ds
            self.scan_thread.fast_axis_array = np.linspace(0, 5, 256)
            self.scan_thread.slow_axis_array = np.linspace(0, 5, 256)
            self.idg.reset_index()
            self.scan_thread.image_data_generator = self.idg
            self.scan_thread.scan_period = 0.1
            self.scan_thread.start()

    # Traits view
    traits_view = View(
        Item('ip1', style='custom', show_label=False),
        Item('btnStartScan', style='custom', show_label=False),
        resizable=True
    )

    def __init__(self, *args, **kwargs):
        super(Demo, self).__init__(*args, **kwargs)
        self.ip1 = ImagePlotUI()
        self.ds = ImageDataSource()
        self.idg = ImageDataGenerator()

    @on_trait_change('ds, ds.data_source_changed')
    def update_view(self):
        self.ip1.update(self.ds)


def test():
    demo = Demo()
    demo.configure_traits()

if __name__ == '__main__':
    test()
