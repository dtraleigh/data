var ctx = document.getElementById("myChart");
var myChart = new Chart(ctx, {
  type: 'scatter',
  data: chart_data,
  options: {
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: false
        }
      }],
      xAxes: [{
        type: 'time',
        time: {
          unit: 'month'
        }
      }]
    },
    legend: {
      display: true,
    },
    tooltips: {
      callbacks: {
        label: function(tooltipItem, data) {
          return tooltipItem.yLabel;
        },
      }
    }
  }
});