import * as d3 from "d3";
import type {ReportData} from "../../report";
import {extractData} from "./parser";

function createZoomableSVG(width: number, height: number) {
    // Create a container for scrolling and zooming
    const container = d3.select("body").append("div")
        .attr("class", "graph-viewport")
        .style("width", "100%")
        .style("height", "100%")
        .style("overflow", "auto");

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g"); // Append a 'g' element for zooming

    const zoom: any = d3.zoom()
        .scaleExtent([0.1, 10]) // Adjust the zoom scale extent as needed
        .on("zoom", () => {
            svg.attr("transform", d3.event.transform);
        });

    container.call(zoom);

    return {container, svg, zoom};
}

export function renderGraph(report: ReportData, showAllFiles: boolean) {
    // Remove previous graph
    d3.select(".graph-viewport").remove();

    // graph = graph.overlaps_report;
    const {nodes, links} = extractData(report, showAllFiles);

    // Set the initial width and height
    const initialWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    const initialHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

    // Create the SVG container and apply zoom/pan functionality
    const {container: any, svg: any, zoom: any} = createZoomableSVG(initialWidth, initialHeight);

    // Create the force simulation
    const force = createForceSimulation(nodes, links, initialWidth, initialHeight);

    // Create color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Render links within the SVG
    renderLinks(svg, links, report);

    // Render nodes with labels within the SVG
    const nodesWithLabels = renderNodesWithLabels(svg, nodes, color, force, report);

    // Update positions on simulation "tick"
    force.on("tick", () => {
        svg.selectAll(".link")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        // Update node and label positions
        nodesWithLabels.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    let stats = calculateStats(links, nodes);
    displayStatistics(stats);
}

