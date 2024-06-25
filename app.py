from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify
from vtkmodules.all import *

# -----------------------------------------------------------------------------
# Trame initialization
# ----------------------------------------------------------------------------

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller
state.trame__title = "Demo Viewer"

# -----------------------------------------------------------------------------
# Reading pipeline
# ----------------------------------------------------------------------------

reader = vtkXMLUnstructuredGridReader()
reader.SetFileName("/deploy/final/01_sep.vtu")
# reader.SetFileName("./final/01_sep.vtu")
reader.Update()

data = vtkUnstructuredGrid()
data.ShallowCopy(reader.GetOutput())

grid = vtkUnstructuredGrid()
grid.ShallowCopy(reader.GetOutput())

variables = []
for i in range(data.GetPointData().GetNumberOfArrays()):
    variables.append(data.GetPointData().GetArrayName(i))
data.GetPointData().SetActiveScalars(variables[0])

lut = vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.0)
lut.Build()

data_mapper = vtkDataSetMapper()
data_mapper.SetInputData(data)
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

with SinglePageLayout(server) as layout:
    layout.title.set_text("Demo Viewer")

    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",):
            view = vtk.VtkLocalView(window)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

if __name__ == "__main__":
    server.start()
