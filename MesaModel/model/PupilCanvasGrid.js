/*
 * PupilCanvasModule modifies CanvasModule
 * - increases font size
 * - redraws grid when size changes
 */
var PupilCanvasModule = function(canvas_width, canvas_height, grid_width, grid_height) {
  CanvasModule.call(this, canvas_width, canvas_height, grid_width, grid_height);
  PupilCanvasModule.prototype = Object.create(CanvasModule.prototype);

  this.canvas = $('.world-grid')[0];
  this.context = this.canvas.getContext("2d");
  this.context.font = '12px sans-serif';

  this.interaction_canvas = $('.world-grid')[1];
  this.interaction_context = this.interaction_canvas.getContext("2d");

  this.currentWidth = grid_width;
  this.currentHeight = grid_height;

  // Add connection error overlay to the page
  this.parent = $('.world-grid-parent')[0];
  var tag = `<div id='error-msg-overlay'
  style='display:none;background-color:rgba(0,0,0,0.5);position:fixed;width:100%;height:100%;top:0;left:0;right:0;bottom:0;z-index:10000;'>
    <div id='error-msg'
      style='background:white;position:absolute;top:50%;left:50%;width:300px;transform:translate(-50%,-50%);padding:20px;font-size:larger;text-align:center;'>
        The server has closed the connection; please refresh the page and try again.
    </div>
</div>`;
  this.parent.append($(tag)[0]);

  this.render = function(data) {
    if (data['grid_width'] != this.currentWidth || data['grid_height'] != this.currentHeight) {
      this.currentWidth = data['grid_width']
      this.currentHeight = data['grid_height']
      var gridSize = Math.max(this.currentWidth, this.currentHeight)
      this.interactionHandler = new InteractionHandler(canvas_width, canvas_height, gridSize, gridSize, this.interaction_context);
      this.canvasDraw = new GridVisualization(canvas_width, canvas_height, gridSize, gridSize, this.context, this.interactionHandler);
    }
    // Copied from parent method
		this.canvasDraw.resetCanvas();
		for (var layer in data) {
      if (!isNaN(layer)) { // Only draw 'real' layers, i.e. those with numeric keys
        this.canvasDraw.drawLayer(data[layer]);
      }
    }
		this.canvasDraw.drawGridLines("#eee");
	};
};
