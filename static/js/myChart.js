var randomScalingFactor = function() {
    return Math.round(Math.random() * 100);
};

var config = {
    type: 'line',
    data: chart_data,
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Chart with Multiline Labels'
        },
    }
};

window.onload = function() {
    var ctx = document.getElementById('myChart').getContext('2d');
    window.myLine = new Chart(ctx, config);
}


/*
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
        title: {
          display: true,
          text: 'Month'
        },
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
});*/