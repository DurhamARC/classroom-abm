from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement


class simElement(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return


def simclass_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return None

    portrayal = {"Shape": "circle", "r": 0.8, "Filled": "true", "Layer": 0}
    type = agent.get_type()

    if type == 3:
        portrayal["Color"] = ["red", "red"]
        portrayal["stroke_color"] = "#00FF00"

    if type == 2:
        portrayal["Color"] = ["yellow", "yellow"]
        portrayal["stroke_color"] = "#00FF00"
    if type == 1:
        portrayal["Color"] = ["green", "green"]
        portrayal["stroke_color"] = "#000000"

    return portrayal


def create_canvas_grid(grid_params):
    return CanvasGrid(simclass_draw, grid_params.width, grid_params.height, 400, 400)


def hist(model):
    Average = model.model_datacollector.get_model_vars_dataframe()
    Average.plot()


sim_element = simElement()
sim_chart = ChartModule(
    [
        {"Label": "Learning Students", "Color": "green"},
        {"Label": "Disruptive Students", "Color": "red"},
        {"Label": "Average End Math", "Color": "black"},
    ],
    data_collector_name="model_datacollector",
)
