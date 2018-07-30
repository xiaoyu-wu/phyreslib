from numpy import linspace, zeros
from traits.api import HasTraits, Str, Array, Event


class LineDataSource(HasTraits):
    """ Standard data source for ImagePlotUI
    """
    xs = Array
    ys = Array

    x_unit = Str
    y_unit = Str

    line_name = Str
    metadata = Str
    last_update = Str
    data_source_changed = Event

    def __init__(self, *args, **kwargs):
        super(LineDataSource, self).__init__(*args, **kwargs)

    def _anytrait_changed(self, name, value):
        if name in ['xs', 'ys', 'zs', 'x_unit', 'y_unit', 'z_unit',
                    'image_name', 'metadata', 'last_update']:
            self.data_source_changed = True