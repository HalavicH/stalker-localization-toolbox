// ---------------------- UTILITY FUNCTIONS ----------------------

/**
 * Extract nodes and links from the provided data graph
 * @param {Object} graph
 * @returns {Object} An object containing nodes and links
 */

import {getFileName, prepareDivsWithIds, handleDiffButton, getReportData, hasReportUpdates} from "/static/utils.js";
import {nodeIsNeighbor, hashCode, dragStarted, dragged, dragEnded} from "/static/misc.js";
import {displayNodeDetails, displayLinkDetails, displayStatistics, copySelfToClipboard, showNotification} from "/static/infoProvider.js"
import {renderLinks, renderNodesWithLabels} from "/static/renderer.js"

let show_all_files = false;
let lastReport = undefined;

// Create nodes array from graph.file_to_string_mapping
function createNodesArray(graph) {
    const nodes = [];
    const nodeMap = {}; // Use a map to keep track of nodes
    let index = 0;

    for (const file in graph.file_to_string_mapping) {
        const hasDuplicates = !!graph.overlaps_report[file]; // Check if the file has duplicates
        if (!show_all_files && !hasDuplicates) {
            continue;
        }

        nodes.push({
            id: file,
            strings: graph.file_to_string_mapping[file],
            index: index,
            totalKeysCnt: graph.file_to_string_mapping[file].length,
            hasDuplicates: hasDuplicates // Set hasDuplicates based on whether the file has duplicates
        });

        nodeMap[file] = index; // Add the node to the map
        index++;
    }

    return {nodes, nodeMap}; // Return both the nodes array and the node map
}

// Modify the extractData function to include all nodes
function extractData(graph) {
    const {nodes, nodeMap} = createNodesArray(graph); // Use the modified function
    const links = [];
    let index = nodes.length; // Start the index for links after adding all nodes

    for (const file in graph.overlaps_report) {
        console.log("Source file: " + file);
        const sourceIndex = nodeMap[file]; // Get the index of the source node
        console.log("Source index: " + sourceIndex);

        for (const overlapFile in graph.overlaps_report[file].overlaps) {
            console.log("Target file: " + overlapFile);
            const targetIndex = nodeMap[overlapFile]; // Get the index of the target node
            console.log("Target index: " + targetIndex);

            const overlapInfo = graph.overlaps_report[file].overlaps[overlapFile];

            // Calculate a hash based on the sorted list of duplicated strings
            const hash = Math.abs(hashCode(overlapInfo.overlapping_ids.sort().join("")));
            let msg = hash + " " + overlapInfo.overlapping_ids.sort().join("");

            links.push({
                source: sourceIndex,
                target: targetIndex,
                duplicateKeysCnt: overlapInfo.match_count,

                duplicateKeys: overlapInfo.overlapping_ids,
                color: d3.schemeCategory10[hash % 10], // Use a color from the scheme based on the hash
            });

            index++;
        }
    }

    return {nodes, links};
}


// ---------------------- MAIN RENDER FUNCTION ----------------------
function renderGraph(graph) {
    // Remove previous graph
    d3.select(".graph-viewport").remove();

    // graph = graph.overlaps_report;
    const {nodes, links} = extractData(graph);

    // Set the initial width and height
    const initialWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    const initialHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

    // Create the SVG container and apply zoom/pan functionality
    const {container, svg, zoom} = createZoomableSVG(initialWidth, initialHeight);

    // Create the force simulation
    const force = createForceSimulation(nodes, links, initialWidth, initialHeight);

    // Create color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Render links within the SVG
    renderLinks(svg, links);

    // Render nodes with labels within the SVG
    const nodesWithLabels = renderNodesWithLabels(svg, nodes, color, force, graph);

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

function createZoomableSVG(width, height) {
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

    const zoom = d3.zoom()
        .scaleExtent([0.1, 10]) // Adjust the zoom scale extent as needed
        .on("zoom", () => {
            svg.attr("transform", d3.event.transform);
        });

    container.call(zoom);

    return {container, svg, zoom};
}

function createForceSimulation(nodes, links, width, height) {
    return d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links)
            .distance(d => (1 / d.duplicateKeysCnt) * 100 + 100)
            .strength(d => 1 / (d.duplicateKeysCnt + 1)) // Adjust the strength based on duplicate count
        )
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));
}


function calculateStats(links, nodes) {
    const numNodes = nodes.length
    // Calculate statistics
    const numDups = d3.set(links.flatMap(d => [d.source.id, d.target.id])).size();
    const numNoDups = numNodes - numDups;
    const numLinks = links.length;

    const uniqueDuplicates = new Set();

    links.forEach(link => {
        link.duplicateKeys.forEach(key => {
            uniqueDuplicates.add(key);
        });
    });

    const totalDuplicates = uniqueDuplicates.size;
    return {numNoDups, numDups, numNodes, numLinks, totalDuplicates};
}

// ---------------------- INITIALIZE GRAPH ----------------------

//d3.json("visualization_data.json").then(renderGraph);
//data = {{ data_json|safe }}
getReportData().then((report) => {
    lastReport = report;
    renderGraph(report);
});

// Add an event handler to hide the "Details" overlay when clicking outside of nodes/links
document.addEventListener("click", function (event) {
    const detailsOverlay = document.getElementById("details");
    if (
        !event.target.closest(".node") &&
        !event.target.classList.contains("link") &&
        !event.target.closest(".overlay") && // Check the target's parents for overlay class
        !event.target.closest(".status-bar") // Check the target's parents for status-bar class
    ) {
        // Clicked outside of nodes and links, hide the overlay
        detailsOverlay.style.visibility = "hidden";
    }
});

document.querySelector("#show-all-files").addEventListener("change", (evt) => {
    let checkbox = evt.target;
    if (checkbox.checked) {
        show_all_files = true;
        document.querySelector("#legend-grey-files").style.opacity = "1";
    } else {
        show_all_files = false;
        document.querySelector("#legend-grey-files").style.opacity = "0";
    }

    renderGraph(lastReport)
})

// Setup
setInterval(async () => {
    let hasNew = await hasReportUpdates();
    if (hasNew === false) {
        console.info("Nothing changed so far");
        return;
    }

    let newReport = await getReportData();
    console.info("New data! Let's re-render it");
    showNotification(`<div>Detected changes in files! Refreshing the graph!</div>`);
    lastReport = newReport;
    renderGraph(lastReport);
}, 2000);
