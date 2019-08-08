# Standard library imports

# Major library imports
from numpy import exp, linspace, meshgrid, array, errstate

# Enthought library imports
from traits.api import (
    HasTraits, Instance, Enum, Trait, Callable, on_trait_change
)
from traitsui.api import Item, View, Group, UItem
from chaco.api import (
    ArrayPlotData, CMapImagePlot, ColorBar, LinearMapper, HPlotContainer,
    GridDataSource, ImageData, DataRange2D, DataRange1D, GridMapper, PlotAxis
)
from chaco.tools.api import PanTool, ZoomTool
from chaco import default_colormaps
from enable.api import ComponentEditor

from phyreslib.data_source.api import ImageDataSource

colormaps = list(default_colormaps.color_map_name_dict.keys())


class ImagePlotUI(HasTraits):
    # Image data source
    image_data_source = Instance(ImageDataSource)

    # container for all plots
    container = Instance(HPlotContainer)

    # Plot components within this container
    plot = Instance(CMapImagePlot)
    colorbar = Instance(ColorBar)

    # View options
    colormap = Enum(colormaps)

    # Traits view definitions:
    traits_view = View(
        Group(UItem('container', editor=ComponentEditor(size=(500, 450)))),
        resizable=True
    )

    plot_edit_view = View(
        Group(Item('colormap')),
        buttons=["OK", "Cancel"]
    )

    # -------------------------------------------------------------------------
    # Private Traits
    # -------------------------------------------------------------------------

    _image_index = Instance(GridDataSource)
    _image_value = Instance(ImageData)

    _cmap = Trait(default_colormaps.gray, Callable)

    # -------------------------------------------------------------------------
    # Public View interface
    # -------------------------------------------------------------------------

    def __init__(self, image_data_source=None):
        super(ImagePlotUI, self).__init__()
        with errstate(invalid='ignore'):
            self.create_plot()
        self.image_data_source = image_data_source

    def create_plot(self):

        # Create the mapper, etc
        self._image_index = GridDataSource(
            array([]),
            array([]),
            sort_order=("ascending", "ascending"))
        image_index_range = DataRange2D(self._image_index)
        # self._image_index.on_trait_change(self._metadata_changed,
        #                                   "metadata_changed")

        self._image_value = ImageData(data=array([]), value_depth=1)
        image_value_range = DataRange1D(self._image_value)

        # Create the colormapped scalar plot
        self.plot = CMapImagePlot(index=self._image_index,
                                  index_mapper=GridMapper(
                                      range=image_index_range
                                  ),
                                  value=self._image_value,
                                  value_mapper=self._cmap(image_value_range))

        # Add a left axis to the plot
        left = PlotAxis(orientation='left',
                        title="y",
                        mapper=self.plot.index_mapper._ymapper,
                        component=self.plot)
        self.plot.overlays.append(left)

        # Add a bottom axis to the plot
        bottom = PlotAxis(orientation='bottom',
                          title="x",
                          mapper=self.plot.index_mapper._xmapper,
                          component=self.plot)
        self.plot.overlays.append(bottom)

        # Add some tools to the plot
        self.plot.tools.append(PanTool(self.plot,
                                       constrain_key="shift"))
        self.plot.overlays.append(ZoomTool(component=self.plot,
                                           tool_mode="box", always_on=False))

        # Create a colorbar
        cbar_index_mapper = LinearMapper(range=image_value_range)
        self.colorbar = ColorBar(index_mapper=cbar_index_mapper,
                                 plot=self.plot,
                                 padding_top=self.plot.padding_top,
                                 padding_bottom=self.plot.padding_bottom,
                                 padding_right=40,
                                 resizable='v',
                                 width=10)

        # Create a container and add components
        self.container = HPlotContainer(padding=40, fill_padding=True,
                                        bgcolor="white", use_backbuffer=False)
        self.container.add(self.colorbar)
        self.container.add(self.plot)

    @on_trait_change('image_data_source.data_source_changed')
    def update_plot(self):
        xs = self.image_data_source.xs
        ys = self.image_data_source.ys
        zs = self.image_data_source.zs
        self.colorbar.index_mapper.range.low = zs.min()
        self.colorbar.index_mapper.range.high = zs.max()
        self._image_index.set_data(xs, ys)
        self._image_value.data = zs
        self.container.invalidate_draw()
        self.container.request_redraw()

    # -------------------------------------------------------------------------
    # Event handlers
    # -------------------------------------------------------------------------

    def _colormap_changed(self):
        self._cmap = default_colormaps.color_map_name_dict[self.colormap]
        if self.plot is not None:
            value_range = self.plot.color_mapper.range
            self.plot.color_mapper = self._cmap(value_range)
            self.container.request_redraw()
