var RightPanelModule = function() {
	var tag = "<div class='well right-panel'></div>";
	var div = $(tag)[0];

	// Append text tag to #elements:
	$("#elements").append(div);

	this.render = function(data) {
		if (data) {
			$(div).html(data);
			$(div).hide();
		} else {
			$(div).hide();
		}
	};

	this.reset = function() {
		$(div).html("");
	};
};
