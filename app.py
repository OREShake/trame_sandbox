from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify
from vtkmodules.all import *

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

reader = vtkXMLUnstructuredGridReader()
reader.SetFileName("final/01_sep.vtu")
reader.Update()

grid = vtkUnstructuredGrid()
grid.ShallowCopy(reader.GetOutput())

wireframe = vtkUnstructuredGrid()
wireframe.ShallowCopy(reader.GetOutput())

variables = []
for i in range(grid.GetPointData().GetNumberOfArrays()):
    variables.append(grid.GetPointData().GetArrayName(i))
grid.GetPointData().SetActiveScalars(variables[0])

lut = vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.0)
lut.Build()

mapper = vtkDataSetMapper()
mapper.SetInputData(grid)
mapper.SetScalarRange(grid.GetScalarRange())
mapper.SetScalarModeToUsePointData()
mapper.SetColorModeToMapScalars()
mapper.SetLookupTable(lut)

actor = vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetAmbient(0.4)
actor.GetProperty().SetDiffuse(1)

filter = vtkUnstructuredGridGeometryFilter()
filter.SetInputData(wireframe)

edges = vtkExtractEdges()
edges.SetInputConnection(filter.GetOutputPort())

edge_mapper = vtkDataSetMapper()
edge_mapper.SetInputConnection(edges.GetOutputPort())

edge_actor = vtkActor()
edge_actor.SetMapper(edge_mapper)
edge_actor.GetProperty().SetRepresentationToWireframe()
edge_actor.GetProperty().SetColor(0, 0, 0)

renderer = vtkRenderer()
renderer.AddActor(actor)
renderer.AddActor(edge_actor)
renderer.SetBackground(1, 1, 1)
renderer.ResetCamera()

window = vtkRenderWindow()
window.AddRenderer(renderer)
window.OffScreenRenderingOn()

interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

interactor_style = vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(interactor_style)

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


@state.change("variable")
def update_variable(variable, **kwargs):
    grid.GetPointData().SetActiveScalars(variable)
    mapper.SetScalarRange(grid.GetScalarRange())
    color_legend_actor.SetTitle(variable)
    ctrl.view_update()
    print(variable + " was selected")


with SinglePageLayout(server) as layout:
    layout.title.set_text("Ansys Viewer")

    with layout.toolbar:
        vuetify.VSelect(
            v_model=("variable", variables[0]),
            label="Variables",
            items=("options", variables),
            classes="mr-5",
            hide_details=True,
            dense=True,
            style="max-width: 300px"
        )
        vuetify.VSelect(
            v_model=("file", "ver-001"),
            label="Files",
            items=("options", ["ver-001", "ver-002", "ver-003"]),
            hide_details=True,
            dense=True,
            style="max-width: 200px"
        )

    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",):
            view = vtk.VtkLocalView(window)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

if __name__ == "__main__":
    server.start()
