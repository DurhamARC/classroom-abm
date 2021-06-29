from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement

from model.data_types import PupilLearningState


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
    learning_state = agent.get_learning_state()

    if learning_state == PupilLearningState.RED:
        portrayal["Color"] = ["red", "red"]
        portrayal["stroke_color"] = "#00FF00"

    if learning_state == PupilLearningState.YELLOW:
        portrayal["Color"] = ["yellow", "yellow"]
        portrayal["stroke_color"] = "#00FF00"
    if learning_state == PupilLearningState.GREEN:
        portrayal["Color"] = ["green", "green"]
        portrayal["stroke_color"] = "#000000"

    return portrayal


def create_canvas_grid(width, height):
    return CanvasGrid(simclass_draw, width, height, 400, 400)


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
