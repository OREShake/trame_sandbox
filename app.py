from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify
from vtkmodules.all import *
import os

server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

renderer = vtkRenderer()
window = vtkRenderWindow()
interactor = vtkRenderWindowInteractor()

window.AddRenderer(renderer)
window.OffScreenRenderingOn()
interactor.SetRenderWindow(window)

reader = vtkXMLUnstructuredGridReader()
reader.SetFileName("/home/busya/code/trame_sandbox/final/01_sep.vtu")
# reader.SetFileName("./final/01_sep.vtu")
reader.Update()

mapper = vtkDataSetMapper()
mapper.SetInputData(reader.GetOutput())

actor = vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetAmbient(0.4)
actor.GetProperty().SetDiffuse(1)

renderer.AddActor(actor)
renderer.ResetCamera()
renderer.Render()

with SinglePageLayout(server) as layout:
    layout.title.set_text("Ansys Viewer")

    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",):
            view = vtk.VtkRemoteView(window)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

if __name__ == "__main__":
    server.start()
