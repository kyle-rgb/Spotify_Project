function drawStackedArea(data){
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%y-%b-%d").parse;
    //formatPercent = d3.format(".0%");

var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.category20();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    //.tickFormat(formatPercent);

var area = d3.svg.area()
    .x(function(d) { return x(d.date); })
    .y0(function(d) { return y(d.y0); })
    .y1(function(d) { return y(d.y0 + d.y); });

var stack = d3.layout.stack()
    .values(function(d) { return d.values; });

var svg = d3.select("#radars").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

let dataz = {date: ["13-Oct-31", "13-Nov-30", "13-Dec-31"],
Kermit: [113.44, 109.86, 113.46],
piggy: [435.15, 506.85, 644.88],
Gonzo: [19.57, 18.97, 19.57],
fuzzy: [60.55, 58.77, 60.57],
hogthrob: [53.02, 388.37, 669.47],
animal: [268.28, 131.48, 0],
floyd: [87.34, 85.34, 87.46],
Gabriel: [1.98, 1.98, 1.98],
Beaker: [0, 0, 0],
scooter: [31.68, 48.50, 80.97],
statler: [0, 0, 0],
waldorf: [21.59, 21.59, 21.59],
slim: [4.82, 4.7, 4.82],
sam: [11.31, 11.31, 11.43]
}


  color.domain(d3.keys(Object.keys(dataz)).filter(function(key) { return key !== "date"; }));
  dataz.date.forEach(function(d) {
  	d = parseDate(d);
  });

  var browsers = stack(color.domain().map(function(name) {
    return {
      name: name,
      values: function(d){
          for(let i=0; i<dataz.date.length; i++){
            return {date: data.date[i], y: d[name][i] * 1};
          }
      }
        
      
    };
  }));

  // Find the value of the day with highest total value
  var maxDateVal = d3.max(dataz, function(d){
    var vals = d3.keys(d).map(function(key){ return key !== "date" ? d[key] : 0 });
    return d3.sum(vals);
  });

  // Set domains for axes
  x.domain(d3.extent(dataz, function(d) { return d.date; }));
  y.domain([0, maxDateVal])

  var browser = svg.selectAll(".browser")
      .data(browsers)
    .enter().append("g")
      .attr("class", "browser");

  browser.append("path")
      .attr("class", "area")
      .attr("d", function(d) { return area(d.values); })
      .style("fill", function(d) { return color(d.name); });

  browser.append("text")
      .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
      .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.y0 + d.value.y / 2) + ")"; })
      .attr("x", -6)
      .attr("dy", ".35em")
      .text(function(d) { return d.name; });

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);


    console.log("DONESY!")
};