from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets
# from vtkmodules.all import *

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

# cone = vtkConeSource()
# cone.Update()

# mapper = vtkPolyDataMapper()
# mapper.SetInputConnection(cone.GetOutputPort())

# actor = vtkActor()
# actor.SetMapper(mapper)

state.trame__title = "Trame Sandbox"

with SinglePageLayout(server) as layout:
    layout.title.set_text("Hello Trame")

if __name__ == "__main__":
    server.start()
