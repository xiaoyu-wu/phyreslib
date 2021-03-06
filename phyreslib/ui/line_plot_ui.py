# Major library imports
from numpy import array, errstate

# Enthought library imports
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import Group, UItem, View
from enable.component_editor import ComponentEditor
from chaco.api import ArrayPlotData, HPlotContainer, Plot

from phyreslib.data_source.api import LineDataSource


class LinePlotUI(HasTraits):
    # Line data source
    line_data_source = Instance(LineDataSource)

    # container for all plots
    container = Instance(HPlotContainer)

    # Plot components within this container
    line_plot = Instance(Plot)

    # Plot data
    pd = Instance(ArrayPlotData)

    # Traits view definitions:
    traits_view = View(
        Group(UItem('container', editor=ComponentEditor(size=(500, 200)))),
        resizable=True
    )

    # -------------------------------------------------------------------------
    # Private Traits
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Public View interface
    # -------------------------------------------------------------------------

    def __init__(self, line_data_source=None):
        super(LinePlotUI, self).__init__()
        with errstate(invalid='ignore'):
            self.create_plot()
        self.line_data_source = line_data_source

    def create_plot(self):

        self.pd = ArrayPlotData(line_index=array([]),
                                line_value=array([]))

        # Create the colormapped scalar plot
        self.line_plot = Plot(self.pd)
        self.line_plot.plot(("line_index", "line_value"), type="line")

        # Create a container and add components
        self.container = HPlotContainer()
        self.container.add(self.line_plot)

    @on_trait_change('line_data_source.data_source_changed')
    def update(self):
        xs = self.line_data_source.xs
        ys = self.line_data_source.ys
        self.pd.update(line_index=xs, line_value=ys)
        self.container.invalidate_draw()
        self.container.request_redraw()

    # -------------------------------------------------------------------------
    # Event handlers
    # -------------------------------------------------------------------------
