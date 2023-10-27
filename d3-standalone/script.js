// ---------------------- UTILITY FUNCTIONS ----------------------

/**
 * Extract nodes and links from the provided data graph
 * @param {Object} graph
 * @returns {Object} An object containing nodes and links
 */
function extractData(graph) {
    const nodes = [];
    const links = [];
    const nodeMap = {};
    let index = 0;

    for (let file in graph) {
        if (!nodeMap.hasOwnProperty(file)) {
            nodeMap[file] = index;
            nodes.push({id: file});
            index++;
        }

        for (let overlapFile in graph[file].overlaps) {
            if (!nodeMap.hasOwnProperty(overlapFile)) {
                nodeMap[overlapFile] = index;
                nodes.push({id: overlapFile});
                index++;
            }
            links.push({
                source: nodeMap[file],
                target: nodeMap[overlapFile],
                value: graph[file].overlaps[overlapFile].match_count
            });
        }
    }
    return {nodes, links};
}

/**
 * Determines whether two nodes are neighbors
 * @param {Object} nodeA
 * @param {Object} nodeB
 * @returns {boolean}
 */
function nodeIsNeighbor(nodeA, nodeB, links) {
    return links.some(link =>
        (link.source === nodeA && link.target === nodeB) ||
        (link.source === nodeB && link.target === nodeA)
    );
}

// ---------------------- DRAG HANDLERS ----------------------

function dragStarted(d, force) {
    if (!d3.event.active) force.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragEnded(d, force) {
    if (!d3.event.active) force.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// ---------------------- MAIN RENDER FUNCTION ----------------------
function renderGraph(graph) {
    const { nodes, links } = extractData(graph);

    // Set the initial width and height
    const initialWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    const initialHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

    // Create the SVG container and apply zoom/pan functionality
    const { container, svg, zoom } = createZoomableSVG(initialWidth, initialHeight);

    // Create the force simulation
    const force = createForceSimulation(nodes, links, initialWidth, initialHeight);

    // Create color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Render links within the SVG
    renderLinks(svg, links);

    // Render nodes with labels within the SVG
    const nodesWithLabels = renderNodesWithLabels(svg, nodes, color, force);

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
}

function createZoomableSVG(width, height) {
    // Create a container for scrolling and zooming
    const container = d3.select("body").append("div")
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

    return { container, svg, zoom };
}

function createForceSimulation(nodes, links, width, height) {
    return d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).distance(100))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));
}

function renderLinks(svg, links) {
    svg.selectAll(".link")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke-width", d => Math.sqrt(d.value));
}

function renderNodesWithLabels(svg, nodes, color, force) {
    const nodesWithLabels = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node");

    // Append a circle for each node
    nodesWithLabels.append("circle")
        .attr("r", 10) // Increase the radius to give more space for labels
        .attr("data-node-id", d => d.id)
        .attr("class", "circle")
        .style("fill", d => {
            let folder = d.id.split("/").slice(-2, -1)[0];
            return color(folder);
        })
        .call(d3.drag()
            .on("start", d => dragStarted(d, force))
            .on("drag", dragged)
            .on("end", d => dragEnded(d, force))
        )
        // Modify the mouseover and mouseout event handlers to show/hide the label group
        .on("mouseover", function (d) {
            let id = `#label-group-${d.index}`;
            console.log("Mouse in " + id);

            // Select the corresponding label group and make it visible
            let element1 = document.querySelector(id);
            element1.style.opacity = "1";
            element1.style.visibility = "visible"
        })
        .on("mouseout", function (d) {
            let id = `#label-group-${d.index}`;
            console.log("Mouse out " + id);
            // Select the corresponding label group and hide it with a smooth fade-out effect
            let element = document.querySelector(id);
            element.style.opacity = "0";
            element.style.visibility = "hidden";
        });

    // Append text labels on top of the nodes with background rectangles
    nodesWithLabels.each(function (d, i) { // Pass the index 'i' as the second parameter
        const nodeGroup = d3.select(this);

        // Create a unique label group ID based on the node's index
        const labelGroupId = `label-group-${i}`;

        // Append a group for the label
        const labelGroup = nodeGroup.append("g")
            .attr("class", "label-group")
            .attr("id", labelGroupId)
            .attr("transform", "translate(0, -20)");

        // Calculate the width of the label based on its content
        const labelWidth = (d.id.split('/').pop().length * 8) + 6; // 8px per character plus 6px padding

        // Append a background rectangle for each label
        labelGroup.append("rect")
            .attr("class", "label-bg")
            .attr("rx", 5) // Optional: Adds rounded corners to the background rectangle
            .attr("ry", 5) // Optional: Adds rounded corners to the background rectangle
            .style("fill", "white")
            .attr("width", labelWidth) // Set the width based on label content and padding
            .attr("height", 20) // Adjust the height of the background rectangle as needed
            .attr("x", -labelWidth / 2) // Adjust the x-coordinate to center the rectangle behind the label
            .attr("y", -10); // Adjust the y-coordinate to center the rectangle behind the label

        // Append the text label inside the label group
        labelGroup.append("text")
            .attr("class", "label-text")
            .attr("data-label-for", d => d.id)
            .text(d => d.id.split('/').pop()) // Only the file name
            .attr("dy", 5) // Adjust the vertical position to place the label inside the background rectangle
            .attr("text-anchor", "middle");

        // Initially hide the label group
        labelGroup.style("visibility", "hidden");
    });

    return nodesWithLabels;
}

// ---------------------- INITIALIZE GRAPH ----------------------

d3.json("duplicates-report.json").then(renderGraph);
