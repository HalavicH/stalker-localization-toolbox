from flask import Flask, render_template_string
import webbrowser
from threading import Timer

app = Flask(__name__)

# Mock data for our D3.js bar chart
data = [4, 8, 15, 16, 23, 42]

# HTML template with embedded D3.js code
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>D3.js with Flask Demo</title>
    <script src="https://d3js.org/d3.v5.min.js"></script>
</head>
<body>
<div id="chart"></div>
<script>
    // D3.js code to render a simple bar chart
    var data = {{ data|safe }};
    var width = 420, barHeight = 20;

    var x = d3.scaleLinear()
        .domain([0, d3.max(data)])
        .range([0, width]);

    var chart = d3.select("#chart")
        .attr("width", width)
        .attr("height", barHeight * data.length);

    var bar = chart.selectAll("g")
        .data(data)
        .enter().append("g")
        .attr("transform", function(d, i) { return "translate(0," + i * barHeight + ")"; });

    bar.append("rect")
        .attr("width", x)
        .attr("height", barHeight - 1);

    bar.append("text")
        .attr("x", function(d) { return x(d) - 3; })
        .attr("y", barHeight / 2)
        .attr("dy", ".35em")
        .text(function(d) { return d; });
</script>
</body>
</html>
"""

@app.route('/')
def display_chart():
    return render_template_string(template, data=data)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run()
