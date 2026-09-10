import fastapi

class Dify(fastapi.APIRouter):
    def __init__(self):
        super().__init__()

    def get_routes(self):
        pass