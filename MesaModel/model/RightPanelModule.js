var RightPanelModule = function() {
	var tag = "<div class='well right-panel'></div>";
	var div = $(tag)[0];

	// Append text tag to #elements:
	$("#elements").append(div);

	this.render = function(data) {
		$(div).html(data);
	};

	this.reset = function() {
		$(div).html("");
	};
};
