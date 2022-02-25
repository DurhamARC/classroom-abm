var TimeSeriesChartModule = function(series, canvas_width, canvas_height) {
  window.moment.tz.setDefault("UTC");

  ChartModule.call(this, series, canvas_width, canvas_height);
  TimeSeriesChartModule.prototype = Object.create(ChartModule.prototype);

  var canvas = $("#elements").children().last()[0];
  canvas.style.border = "solid #f5f5f5 1px";
  var context = canvas.getContext("2d");

  var convertColorOpacity = function(hex) {

        if (hex.indexOf('#') != 0) {
            return 'rgba(0,0,0,0.1)';
        }

        hex = hex.replace('#', '');
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
        return 'rgba(' + r + ',' + g + ',' + b + ',0.1)';
  };

  // Prep the chart properties and series:
  var datasets = []
  for (var i in series) {
      var s = series[i];
      var new_series = {
          label: s.Label,
          borderColor: s.Color,
          backgroundColor: convertColorOpacity(s.Color),
          data: []
      };
      datasets.push(new_series);
  }

  var chartData = {
      labels: [],
      datasets: datasets
  };

  var chartOptions = {
      responsive: true,
      tooltips: {
          mode: 'index',
          intersect: false
      },
      hover: {
          mode: 'nearest',
          intersect: true
      },
      scales: {
          xAxes: [{
              type: 'time',
              display: true,
              scaleLabel: {
                  display: true
              },
              ticks: {
                  maxTicksLimit: 11
              },
              time: {
                  tooltipFormat: 'ddd DD MMM HH:mm'
              }
          }],
          yAxes: [{
              display: true,
              scaleLabel: {
                  display: true
              }
          }]
      }
  };

  var chart = new Chart(context, {
      type: 'line',
      data: chartData,
      options: chartOptions
  });

  this.render = function(data) {
      for (i = 0; i < data.length; i++) {
          chart.data.labels.push(new Date(data[i][0]*1000));
          chart.data.datasets[i].data.push(data[i][1]);
      }
      chart.update();
  };

  this.reset = function() {
      while (chart.data.labels.length) { chart.data.labels.pop(); }
      chart.data.datasets.forEach(function(dataset) {
          while (dataset.data.length) { dataset.data.pop(); }
      });
      chart.update();
  };

}
