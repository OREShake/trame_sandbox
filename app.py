from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify
from vtkmodules.all import *

# -----------------------------------------------------------------------------
# Trame initialization
# ----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller
state.trame__title = "Demo Viewer"

# -----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def UpdateBounds(bounds):
    x_expand = (bounds[1] - bounds[0]) * 0.05
    y_expand = (bounds[3] - bounds[2]) * 0.05
    z_expand = (bounds[5] - bounds[4]) * 0.05
    expand = (x_expand + y_expand + z_expand) / 3

    return [bounds[0] - expand, bounds[1] + expand,
            bounds[2] - expand, bounds[3] + expand,
            bounds[4] - expand, bounds[5] + expand]

# -----------------------------------------------------------------------------
# Reading pipeline
# ----------------------------------------------------------------------------


reader = vtkXMLUnstructuredGridReader()
# reader.SetFileName("/deploy/final/01_sep.vtu")
reader.SetFileName("./final/02.vtu")
reader.Update()

data = vtkUnstructuredGrid()
data.ShallowCopy(reader.GetOutput())

grid = vtkUnstructuredGrid()
grid.ShallowCopy(reader.GetOutput())

variables = []
for i in range(data.GetPointData().GetNumberOfArrays()):
    variables.append(data.GetPointData().GetArrayName(i))
data.GetPointData().SetActiveScalars(variables[0])

data.GetPointData().SetActiveVectors("Total Displacement")
grid.GetPointData().SetActiveVectors("Total Displacement")

data_filter = vtkWarpVector()
data_filter.SetInputData(data)
data_filter.SetScaleFactor(3)
data_filter.Update()

lut = vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.0)
lut.Build()

data_mapper = vtkDataSetMapper()
data_mapper.SetInputData(data_filter.GetOutput())
data_mapper.SetScalarRange(data.GetScalarRange())
data_mapper.SetScalarModeToUsePointData()
data_mapper.SetColorModeToMapScalars()
data_mapper.SetLookupTable(lut)

data_actor = vtkActor()
data_actor.SetMapper(data_mapper)
data_actor.GetProperty().SetAmbient(0.4)
data_actor.GetProperty().SetDiffuse(1)

grid_filter = vtkUnstructuredGridGeometryFilter()
grid_filter.SetInputData(grid)

grid_extracter = vtkExtractEdges()
grid_extracter.SetInputConnection(grid_filter.GetOutputPort())

grid_mapper = vtkDataSetMapper()
grid_mapper.SetInputConnection(grid_extracter.GetOutputPort())

grid_actor = vtkActor()
grid_actor.SetMapper(grid_mapper)
grid_actor.GetProperty().SetRepresentationToWireframe()
grid_actor.GetProperty().SetColor(0, 0, 0)

# -----------------------------------------------------------------------------
# Visualization space
# ----------------------------------------------------------------------------

renderer = vtkRenderer()
renderer.AddActor(data_actor)
renderer.AddActor(grid_actor)
renderer.SetBackground(1, 1, 1)
renderer.ResetCamera()

window = vtkRenderWindow()
window.AddRenderer(renderer)
window.OffScreenRenderingOn()
window.Render()

interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

# -----------------------------------------------------------------------------
# Widgets
# ----------------------------------------------------------------------------

# cube_axes = vtkCubeAxesActor()
# cube_axes.SetBounds(UpdateBounds(data.GetBounds()))
# cube_axes.SetCamera(renderer.GetActiveCamera())
# cube_axes.SetXLabelFormat("%6.1f")
# cube_axes.SetYLabelFormat("%6.1f")
# cube_axes.SetZLabelFormat("%6.1f")
# cube_axes.SetFlyModeToOuterEdges()
# cube_axes.GetXAxesLinesProperty().SetColor(0, 0, 0)
# cube_axes.GetYAxesLinesProperty().SetColor(0, 0, 0)
# cube_axes.GetZAxesLinesProperty().SetColor(0, 0, 0)
# renderer.AddActor(cube_axes)

color_legend_actor = vtkScalarBarActor()
color_legend_actor.SetLookupTable(lut)
color_legend_actor.GetLabelTextProperty().SetColor(0, 0, 0)
color_legend_actor.GetTitleTextProperty().SetColor(0, 0, 0)
color_legend_actor.SetTitle(variables[0])
renderer.AddActor2D(color_legend_actor)

color_legend_widget = vtkScalarBarWidget()
color_legend_widget.SetInteractor(interactor)
color_legend_widget.SetScalarBarActor(color_legend_actor)
color_legend_widget.On()

# -----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------


@state.change("variable")
def update_variable(variable, **kwargs):
    data.GetPointData().SetActiveScalars(variable)
    data_mapper.SetScalarRange(data.GetScalarRange())
    color_legend_actor.SetTitle(variable)
    ctrl.view_update()
    print(variable + " was selected")


with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Demo Viewer")

    with layout.drawer as drawer:
        with vuetify.VCard():
            vuetify.VCardTitle(
                "Sources",
                classes="grey lighten-1 py-1 grey--text text--lighten-5",
                style="user-select: none; cursor: pointer",
                hide_details=True,
                dense=True,
            )
            content = vuetify.VCardText(classes="py-2")

            vuetify.VCardTitle(
                "Variables",
                classes="grey lighten-1 py-1 grey--text text--lighten-5",
                style="user-select: none; cursor: pointer",
                hide_details=True,
                dense=True,
            )
            content = vuetify.VCardText(classes="py-2")
            vuetify.VSelect(
                v_model=("variable", variables[0]),
                label="Variables",
                items=("options", variables),
                classes="py-2",
                hide_details=True,
                dense=True,
                outlined=True,
            )
            # vuetify.VDivider(classes="mb-n16")
            vuetify.VSlider(
                # v_model=("mesh_opacity", 1.0),
                min=0,
                max=1,
                step=0.1,
                ticks="always",
                thumb_label="true",
                thumb_size=40,
                label="Time",
                hide_details=True,
                dense=True,
            )
        pass

    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",):
            view = vtk.VtkLocalView(window)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

if __name__ == "__main__":
    server.start()
