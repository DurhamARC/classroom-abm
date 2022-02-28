var CssModule = function() {
	var tag = '<link href="/local/model/custom.css" type="text/css" rel="stylesheet">';
	var link = $(tag);

	// Append css link tag to #elements:
	$("#elements").append(link);

	this.render = function(data) {
	};

	this.reset = function() {
	};
};
