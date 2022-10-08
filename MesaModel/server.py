import json

from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import VisualizationElement

from model.data_types import PupilLearningState


class CssElement(VisualizationElement):
    local_includes = ["model/CssModule.js"]
    js_code = "elements.push(new CssModule());"


class RightPanelElement(VisualizationElement):
    local_includes = ["model/RightPanelModule.js"]
    js_code = "elements.push(new RightPanelModule());"


class TeacherMonitorElement(RightPanelElement):
    def __init__(self):
        pass

    def render(self, model):
        return f"""
<h4>Model Variables</h4>
<table>
    <tr><td>Teacher quality</td><td class="number">{model.teacher_quality.current_value:.2f}</td></tr>
    <tr><td>Teacher control</td><td class="number">{model.teacher_control.current_value:.2f}</td></tr>
    <tr><td>Current date</td><td class="number">{model.current_date}</td></tr>
</table>
"""


class PupilMonitorElement(RightPanelElement):
    def __init__(self):
        self.data = ""

    def render(self, model):
        if model.pupil_state_datacollector:
            self.data = """
<h4>Pupil Learning States</h4>
<table>
    <tr><th>State</th><th class="number"># Pupils</th></tr>
"""
            for k in model.pupil_state_datacollector.model_vars:
                self.data += f"""        <tr>
        <td>{k}</td>
        <td class="number">{model.pupil_state_datacollector.model_vars[k][-1]}</td>
    </tr>
"""

            self.data += "</table>"
        return self.data


class ClassMonitorElement(RightPanelElement):
    def __init__(self):
        self.data = ""

    def render(self, model):
        if model.class_summary_data is not None and not model.class_summary_data.empty:
            self.data = f"""
<h4>Class details</h4>
<table>
    <tr>
        <td>Total pupils</td>
        <td class="number">{model.class_summary_data.iloc[0]['total_pupils']}</td>
    </tr>
    <tr>
        <td>Pupils taking free school meals</td>
        <td class="number">{model.class_summary_data.iloc[0]['fsm_pupils']}</td>
    </tr>
    <tr>
        <td>Pupils from ethnic minorities</td>
        <td class="number">{model.class_summary_data.iloc[0]['ethnic_minority_pupils']}</td>
    </tr>
    <tr>
        <td>Pupils with special educational needs</td>
        <td class="number">{model.class_summary_data.iloc[0]['sen_pupils']}</td>
    </tr>

    <tr>
        <td>Boys</td>
        <td class="number">{model.class_summary_data.iloc[0]['total_pupils'] - model.class_summary_data.iloc[0]['girls']}</td>
    </tr>
</table>
"""
        else:
            self.data = ""

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

        self.js_code = (
            f"elements.push({new_element});"
            + """
// Add an onclose event to the WebSocket instance to show a message to the user
$(document).ready(function(){
    ws.onclose = function(...args) {
      $('#error-msg-overlay').show();
    }
});
"""
        )

    def render(self, model):
        data = super().render(model)
        data["grid_width"] = model.grid.width
        data["grid_height"] = model.grid.height
        return data


class CustomChartModule(ChartModule):

    package_includes = ["ChartModule.js"]
    local_includes = [
        "model/MomentTzChart.min.js",
        "model/TimeSeriesChartModule.js",
    ]

    def __init__(
        self,
        series,
        canvas_height=200,
        canvas_width=500,
        data_collector_name="datacollector",
    ):
        super().__init__(series, canvas_height, canvas_width, data_collector_name)
        series_json = json.dumps(self.series)
        new_element = "new TimeSeriesChartModule({}, {},  {})"
        new_element = new_element.format(series_json, canvas_width, canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    # Override render method so if the data collector no longer exists,
    # the chart remains as it is
    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)
        if data_collector:

            for s in self.series:
                name = s["Label"]
                try:
                    date = data_collector.model_vars["Date"][-1]
                    val = data_collector.model_vars[name][-1]  # Latest value
                except (IndexError, KeyError):
                    val = (0, 0)
                current_values.append((date, val))
            return current_values
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
