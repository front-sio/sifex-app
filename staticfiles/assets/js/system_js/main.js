
  const renderMasterAwbChart = (data, labels) => {
    const ctx2 = document.getElementById("chart-2").getContext("2d");
    const myChart2 = new Chart(ctx2, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "last week",
            data: data,
            backgroundColor: [
              "rgba(54, 162, 235, 1)",
              "rgba(255, 99, 132, 1)",
              "rgba(255, 206, 86, 1)",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        indexAxis:'y',maintainAspectRatio:false,legend:{display:false,labels:{display:false}},scales:{yAxes:[{ticks:{beginAtZero:true,fontSize:11,}}],xAxes:[{ticks:{beginAtZero:true,fontSize:11,max:80}}]}}
    });
  }



  const renderSlaveAwbChart = (data, labels) => {
    const ctx1 = document.getElementById("chart-1").getContext("2d");
    const myChart = new Chart(ctx1, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Last month kg",
            data: data,
            backgroundColor: [
              "rgba(54, 162, 235, 1)",
              "rgba(255, 99, 132, 1)",
              "rgba(255, 206, 86, 1)",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        
      },
    });
  
  
  
  }


  const renderArrivalAwbChart = (data, labels) => {
    const ctx3 = document.getElementById("chart-3").getContext("2d");
    const myChart3 = new Chart(ctx3, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Last month kg",
            data: data,
            backgroundColor: [
              "rgba(54, 162, 235, 1)",
              "rgba(255, 99, 132, 1)",
              "rgba(255, 206, 86, 1)",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        
      },
    });
  
  
  
  }
  
  
  const getSlaveAwbChartData = () => {
    fetch('/sifex/total_month_master_awb_kg/').then(res=>res.json()).then((results)=>{
      console.log('results', results)
  
      const awb_type_data = results.awb_type_data
  
      const [labels, data] = [
        Object.keys(awb_type_data),
        Object.values(awb_type_data),
      ]
  
      renderSlaveAwbChart(data, labels)
    })
  }



  const getArrivalAwbChartData = () => {
    fetch('/sifex/total_month_master_awb_kg/').then(res=>res.json()).then((results)=>{
      console.log('results', results)
  
      const awb_type_data = results.awb_type_data
  
      const [labels, data] = [
        Object.keys(awb_type_data),
        Object.values(awb_type_data),
      ]
  
      renderArrivalAwbChart(data, labels)
    })
  }
  
  const getMasterAwbChartData = () => {
    fetch('/sifex/total_master_awb_kg/').then(res=>res.json()).then((results)=>{
      console.log('results', results)
  
      const awb_type_data = results.awb_type_data
  
      const [labels, data] = [
        Object.keys(awb_type_data),
        Object.values(awb_type_data),
      ]
  
      renderMasterAwbChart(data, labels)
    })
  }
  
  document.onload = getMasterAwbChartData()
  document.onload = getSlaveAwbChartData()
  document.onload = getArrivalAwbChartData()









  // dropdown menu

  $(document).ready(function(){
    //jquery for toggle sub menus
    $('.sub-btn').click(function(){
      $(this).next('.sub-menu').slideToggle();
      $(this).find('.dropdown').toggleClass('rotate');
    });
    //jquery for expand and collapse the sidebar
    $('.menu-btn').click(function(){
      $('.side-bar').addClass('active');
      $('.menu-btn').css("visibility", "hidden");
    });
    //Active cancel button
    $('.close-btn').click(function(){
      $('.side-bar').removeClass('active');
      $('.menu-btn').css("visibility", "visible");
    });
  });