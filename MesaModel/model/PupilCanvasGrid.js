/*
 * PupilCanvasModule inherits CanvasModule but modifies the font 
 */
var PupilCanvasModule = function(canvas_width, canvas_height, grid_width, grid_height) {
  canvasModule = CanvasModule.call(this, canvas_width, canvas_height, grid_width, grid_height);

  var canvas = $('.world-grid')[0];
	var context = canvas.getContext("2d");
  context.font = '12px sans-serif';
};
