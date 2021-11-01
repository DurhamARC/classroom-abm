from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import VisualizationElement

from model.data_types import PupilLearningState


class RightPanelElement(VisualizationElement):
    local_includes = ["model/RightPanelModule.js"]
    js_code = "elements.push(new RightPanelModule());"


class TeacherMonitorElement(RightPanelElement):
    def __init__(self):
        pass

    def render(self, model):
        return f"""
<h4 style="margin-top:0">Teacher Variables</h4>
<table>
    <tr><td style="padding: 5px;">Teacher quality</td><td style="padding: 5px;">{model.teacher_quality:.2f}</td></tr>
    <tr><td style="padding: 5px;">Teacher control</td><td style="padding: 5px;">{model.teacher_control:.2f}</td></tr>
</table>
"""


class PupilMonitorElement(RightPanelElement):
    def __init__(self):
        pass

    def render(self, model):
        pupil_data = model.pupil_datacollector.model_vars["Pupils"][-1]
        data = """
<h4 style="margin-top:0">Pupil Maths Scores</h4>
<table>
    <tr><th style="padding: 5px;">Pupil</th><th style="padding: 5px;text-align:right;">Score</th><th style="padding: 5px;text-align:right;">Change</th></tr>
"""
        for k in ["Highest", "Mid", "Lowest"]:
            data += f"""        <tr>
            <td style="padding: 5px;">{k}</td>
            <td style="padding: 5px;text-align:right;">{pupil_data[model.pupils_to_watch[k]][0]:.2f}</td>
            <td style="padding: 5px;text-align:right;">{pupil_data[model.pupils_to_watch[k]][1]:.2f}</td>
        </tr>
"""

        data += "</table>"
        return data


class PupilCanvasGrid(CanvasGrid):
    """
    Modification of CanvasGrid to allow us to change the font size of the canvas text
    """

    local_includes = ["model/PupilCanvasGrid.js"]

    def __init__(
        self,
        portrayal_method,
        grid_width,
        grid_height,
        canvas_width=500,
        canvas_height=500,
    ):
        super().__init__(
            portrayal_method, grid_width, grid_height, canvas_width, canvas_height
        )

        new_element = "new PupilCanvasModule({}, {}, {}, {})".format(
            self.canvas_width, self.canvas_height, self.grid_width, self.grid_height
        )

        self.js_code = "elements.push(" + new_element + ");"


def simclass_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return None

    portrayal = {
        "Shape": "model/lc_person_120_yellow.png",
        "scale": 1.0,
        "Layer": 0,
        "text": round(agent.e_math, 1),
        "text_color": "#000000",
    }
    learning_state = agent.get_learning_state()

    if learning_state == PupilLearningState.RED:
        portrayal["Shape"] = "model/lc_person_120_red.png"
    elif learning_state == PupilLearningState.GREEN:
        portrayal["Shape"] = "model/lc_person_120_green.png"

    return portrayal


def create_canvas_grid(width, height):
    return PupilCanvasGrid(simclass_draw, width, height, 400, 400)


def hist(model):
    Average = model.model_datacollector.get_model_vars_dataframe()
    Average.plot()


sim_element = TeacherMonitorElement()
sim_chart = ChartModule(
    [
        {"Label": "Learning Students", "Color": "green"},
        {"Label": "Disruptive Students", "Color": "red"},
        {"Label": "Average End Math", "Color": "black"},
    ],
    data_collector_name="model_datacollector",
)
