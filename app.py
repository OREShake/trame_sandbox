from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout

server = get_server(client_type="vue2")

with SinglePageLayout(server) as layout:
    layout.title.set_text("Trame Example")

if __name__ == "__main__":
    server.start()
