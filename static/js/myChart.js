var ctx = document.getElementById('myChart');
var myChart = new Chart(ctx, {
  type: 'scatter',
  data: chart_data,
  options: {
    scales: {
      y: [{
        ticks: {
          beginAtZero: false
        }
      }],
      x: [{
        labels: ['test1', 'test2'],
        type: 'time',
        display: true,
        title: {
          display: true,
          text: 'Month'
        },
        time: {
          minUnit: 'month'
        },
        ticks: {
          source: 'labels'
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