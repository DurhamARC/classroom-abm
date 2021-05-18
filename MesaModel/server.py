import numpy as np
from mesa.visualization.ModularVisualization import VisualizationElement
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement


class HistogramModule(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["HistogramModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins, canvas_width, canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        agent_maths = [agent.s_math for agent in model.schedule.agents]
        ave = model.datacollector.get_model_vars_dataframe()
        ave.drop(columns=["distruptive", "learning", "Average"])
        x = sum(agent_maths)
        N = len(agent_maths)
        B = x / N
        hist = np.histogram(ave, bins=self.bins)[0]
        return [int(x) for x in hist]


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
        return
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
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
    Average = model.datacollector.get_model_vars_dataframe()
    Average.plot()


sim_element = simElement()
sim_chart = ChartModule(
    [
        {"Label": "Learning Students", "Color": "green"},
        {"Label": "Disruptive Students", "Color": "red"},
        {"Label": "Average End Math", "Color": "black"},
    ]
)

histogram = HistogramModule(list(range(10)), 200, 500)
