$(function() {
    'use strict';

    // Function to safely initialize charts
    function initChart(chartId, chartConfig) {
        var element = document.getElementById(chartId);
        if (element) {
            var ctx = element.getContext('2d');
            return new Chart(ctx, chartConfig);
        } else {
            console.log('Chart element not found: ' + chartId + ', skipping...');
            return null;
        }
    }

    // Chart Bar 1
    initChart('chartBar1', {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Sales',
                data: [24, 10, 32, 24, 26, 20],
                backgroundColor: '#664dc9'
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            legend: { display: false, labels: { display: false } },
            scales: {
                yAxes: [{ ticks: { beginAtZero: true, fontSize: 10, max: 80 } }],
                xAxes: [{ barPercentage: 0.6, ticks: { beginAtZero: true, fontSize: 11 } }]
            }
        }
    });

    // Chart Bar 2
    initChart('chartBar2', {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Sales',
                data: [14, 12, 34, 25, 24, 20],
                backgroundColor: '#44c4fa'
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            legend: { display: false, labels: { display: false } },
            scales: {
                yAxes: [{ ticks: { beginAtZero: true, fontSize: 10, max: 80 } }],
                xAxes: [{ barPercentage: 0.6, ticks: { beginAtZero: true, fontSize: 11 } }]
            }
        }
    });

    // Chart Bar 3 (with gradient)
    var ctx3Element = document.getElementById('chartBar3');
    if (ctx3Element) {
        var ctx3 = ctx3Element.getContext('2d');
        var gradient = ctx3.createLinearGradient(0, 0, 0, 250);
        gradient.addColorStop(0, '#44c4fa');
        gradient.addColorStop(1, '#664dc9');
        
        new Chart(ctx3, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Sales',
                    data: [14, 12, 34, 25, 24, 20],
                    backgroundColor: gradient
                }]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                legend: { display: false, labels: { display: false } },
                scales: {
                    yAxes: [{ ticks: { beginAtZero: true, fontSize: 10, max: 80 } }],
                    xAxes: [{ barPercentage: 0.6, ticks: { beginAtZero: true, fontSize: 11 } }]
                }
            }
        });
    }

    // Other charts with safe initialization...
    var datapie = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        datasets: [{
            data: [35, 20, 8, 15, 24],
            backgroundColor: ['#664dc9', '#44c4fa', '#38cb89', '#3e80eb', '#ffab00', '#ef4b4b']
        }]
    };

    var optionpie = {
        maintainAspectRatio: false,
        responsive: true,
        legend: { display: false },
        animation: { animateScale: true, animateRotate: true }
    };

    initChart('chartPie', {
        type: 'doughnut',
        data: datapie,
        options: optionpie
    });

    initChart('chartDonut', {
        type: 'pie',
        data: datapie,
        options: optionpie
    });
});