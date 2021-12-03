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
<h4 style="margin-top:0">Model Variables</h4>
<table>
    <tr><td style="padding: 5px;">Teacher quality</td><td style="padding: 5px;">{model.teacher_quality:.2f}</td></tr>
    <tr><td style="padding: 5px;">Teacher control</td><td style="padding: 5px;">{model.teacher_control:.2f}</td></tr>
    <tr><td style="padding: 5px;">Current date</td><td style="padding: 5px;">{model.current_date}</td></tr>
</table>
"""


class PupilMonitorElement(RightPanelElement):
    def __init__(self):
        self.data = ""

    def render(self, model):
        if model.pupil_state_datacollector:
            self.data = """
<h4 style="margin-top:0">Pupil Learning States</h4>
<table>
    <tr><th style="padding: 5px;">State</th><th style="padding: 5px;text-align:right;"># Pupils</th></tr>
"""
            for k in model.pupil_state_datacollector.model_vars:
                self.data += f"""        <tr>
        <td style="padding: 5px;">{k}</td>
        <td style="padding: 5px;text-align:right;">{model.pupil_state_datacollector.model_vars[k][-1]}</td>
    </tr>
"""

            self.data += "</table>"
        return self.data


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

    def render(self, model):
        data = super().render(model)
        data["grid_width"] = model.grid.width
        data["grid_height"] = model.grid.height
        return data


class CustomChartModule(ChartModule):

    # Override render method so if the data collector no longer exists,
    # the chart remains as it is
    def render(self, model):
        data_collector = getattr(model, self.data_collector_name)
        if data_collector:
            return super().render(model)
        else:
            return []


def simclass_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return None

    portrayal = {
        "Shape": "model/lc_person_120_yellow.png",
        "Layer": 0,
        "text": round(agent.e_math, 1),
        "text_color": "#000000",
        "Inattentiveness": round(agent.inattentiveness, 1),
        "Hyperactivity/impulsivity": round(agent.hyper_impulsive, 1),
        "Deprivation": round(agent.deprivation, 1),
        "Ability": round(agent.ability, 2),
        "Start Maths Score": round(agent.s_math, 1),
        "Current Maths Score": round(agent.e_math, 1),
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
    maths_scores = model.maths_datacollector.get_model_vars_dataframe()
    maths_scores.plot()


sim_element = TeacherMonitorElement()
sim_chart = CustomChartModule(
    [
        {"Label": "Mean Score", "Color": "orange"},
    ],
    data_collector_name="maths_datacollector",
)
