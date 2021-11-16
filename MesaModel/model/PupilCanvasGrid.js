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

  this.render = function(data) { // FIXME: see if we can call actual method
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
