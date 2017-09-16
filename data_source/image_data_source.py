from numpy import linspace, zeros
from traits.api import HasTraits, Str, Array, Event


class ImageDataSource(HasTraits):
    """ Standard data source for ImagePlotUI
    """
    xs = Array
    ys = Array
    zs = Array
    x_unit = Str
    y_unit = Str
    z_unit = Str
    image_name = Str
    metadata = Str
    last_update = Str
    data_source_changed = Event

    def __init__(self, *args, **kwargs):
        super(ImageDataSource, self).__init__(*args, **kwargs)
        self.xs = linspace(0, 1, 256)
        self.ys = linspace(0, 1, 256)
        self.zs = zeros((256,256))

    def _anytrait_changed(self, name, value):
        if name in ['xs', 'ys', 'zs', 'x_unit', 'y_unit', 'z_unit',
                    'image_name', 'metadata', 'last_update']:
            self.data_source_changed = True
