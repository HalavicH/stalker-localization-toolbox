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
    return { nodes, links };
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

    const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    const height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

    const svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    const force = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).distance(100))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Render links
    svg.selectAll(".link")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke-width", d => Math.sqrt(d.value));

    // Render nodes
    svg.selectAll(".node")
        .data(nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", 10)
        .attr("data-node-id", d => d.id)
        .style("fill", d => {
            let folder = d.id.split("/").slice(-2, -1)[0];
            return color(folder);
        })
        .call(d3.drag()
            .on("start", d => dragStarted(d, force))
            .on("drag", dragged)
            .on("end", d => dragEnded(d, force))
        )
        .on("mouseover", function(d) {
            // Get the node's unique identifier
            let nodeId = d3.select(this).attr("data-node-id");

            // Select the corresponding label and make it visible
            d3.select(`text[data-label-for='${nodeId}']`)
                .style("visibility", "visible");
        })
        .on("mouseout", function(d) {
            // Get the node's unique identifier
            let nodeId = d3.select(this).attr("data-node-id");

            // Select the corresponding label and hide it
            d3.select(`text[data-label-for='${nodeId}']`)
                .style("visibility", "hidden");
        });

    // Render labels
    svg.selectAll(".labels")
        .data(nodes)
        .enter().append("text")
        .attr("class", "labels")
        .attr("data-label-for", d => d.id)
        .text(d => d.id.split('/').pop());  // Only the file name

    // Update positions on simulation "tick"
    force.on("tick", () => {
        svg.selectAll(".link")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        svg.selectAll(".node")
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        svg.selectAll(".labels")
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
}

// ---------------------- INITIALIZE GRAPH ----------------------

d3.json("duplicates-report.json").then(renderGraph);
