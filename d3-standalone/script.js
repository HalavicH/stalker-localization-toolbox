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
            const overlapInfo = graph[file].overlaps[overlapFile];

            // Calculate a hash based on the sorted list of duplicated strings
            const hash = Math.abs(hashCode(overlapInfo.overlapping_ids.sort().join("")));
            msg = hash + " " + overlapInfo.overlapping_ids.sort().join("");
            console.log(msg);

            links.push({
                source: nodeMap[file],
                target: nodeMap[overlapFile],
                value: overlapInfo.match_count,
                duplicateKeysCnt: overlapInfo.overlapping_ids.length,
                duplicateKeys: overlapInfo.overlapping_ids,
                color: d3.schemeCategory10[hash % 10], // Use a color from the scheme based on the hash
            });
        }
    }

    console.log(links)
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

// Function to calculate a hash code for a string
function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
    }
    return hash;
}

function copySelfToClipboard(element) {
    const textToCopy = element.innerText;

    const textArea = document.createElement("textarea");
    textArea.value = textToCopy;
    document.body.appendChild(textArea);

    textArea.select();
    document.execCommand("copy");

    document.body.removeChild(textArea);

    // // Optionally, you can provide user feedback here
    // alert(`'${textToCopy}' copied to clipboard!`);

    // Show a tooltip or feedback to indicate successful copying (optional)
    showNotification(`
        <div class="status-label">Path copied to clipboard: (Ctrl+V) to paste</div>
        <div class="path">${textToCopy}</div>
    `);
}

// Function to show a notification in the top right corner
function showNotification(html) {
    const notification = document.createElement("div");
    notification.innerHTML = html;
    notification.className = "notification";

    // Append the notification to the body
    document.body.appendChild(notification);

    // Automatically remove the notification after a short delay
    setTimeout(() => {
        notification.style.opacity = "0";
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 2000); // Adjust the delay (in milliseconds) as needed
    }, 2000); // Adjust the delay (in milliseconds) as needed
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

    let stats = calculateStats(links);
    displayStatistics(stats);
}

function displayStatistics(statistics) {
    const infoOverlay = document.getElementById("info");
    infoOverlay.innerHTML = `
        <h2>Info</h2>
        <table>
            <tr>
                <td class="status-label">Nodes (Files):</td>
                <td>${statistics.numNodes}</td>
            </tr>
            <tr>
                <td class="status-label">Links (Duplicates):</td>
                <td>${statistics.numLinks}</td>
            </tr>
            <tr>
                <td class="status-label">Total Duplicates:</td>
                <td>${statistics.totalDuplicates}</td>
            </tr>
        </table>
    `;
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

    return {container, svg, zoom};
}

function createForceSimulation(nodes, links, width, height) {
    return d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).distance(100))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));
}

function calculateStats(links) {
    // Calculate statistics
    const numNodes = d3.set(links.flatMap(d => [d.source.id, d.target.id])).size();
    const numLinks = links.length;
    const totalDuplicates = links.reduce((total, link) => total + link.duplicateKeysCnt, 0);

    return {numNodes, numLinks, totalDuplicates};
}

function renderLinks(svg, links) {
    // Render links within the SVG
    const linkElements = svg.selectAll(".link")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke", d => d.color) // Use the color defined in the link
        .attr("stroke-width", d => Math.sqrt(d.value));

    // Add a tooltip to show the number of duplicate keys when hovering over the link
    linkElements
        .on("mouseover", function (d) {
            const tooltip = d3.select("#tooltip");
            let header = `Duplicate Keys: (Total: ${d.duplicateKeysCnt})<br>`;
            ids = d.duplicateKeys.join("<br>")
            tooltip.html(header + ids);
            tooltip.style("visibility", "visible");
        })
        .on("mousemove", function () {
            const tooltip = d3.select("#tooltip");
            tooltip.style("top", (d3.event.pageY - 10) + "px")
                .style("left", (d3.event.pageX + 10) + "px");
        })
        .on("mouseout", function () {
            const tooltip = d3.select("#tooltip");
            tooltip.style("visibility", "hidden");
        })
        .on("click", function (d) {
            const statusBar = document.getElementById("status-bar");
            statusBar.style.visibility = "visible";

            // Example: Display link information in the status bar
            const statusContent = document.getElementById("status-content");

            statusContent.innerHTML = `
                <div class="status-label">Link From: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.source.id}</div>
                <div class="status-label">Link To: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.target.id}</div>
            `;
        });
}

function renderNodesWithLabels(svg, nodes, color, force, graph) {
    // Determine the maximum total_id_cnt to scale the node size
    const maxTotalIdCount = d3.max(nodes, d => graph[d.id].total_id_cnt);

    // Create a scale function to map total_id_cnt to node size
    const nodeSizeScale = d3.scaleLinear()
        .domain([0, maxTotalIdCount])
        .range([5, 20]); // Adjust the range to your desired minimum and maximum node sizes

    const nodesWithLabels = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node");

    // Append a circle for each node with dynamic radius
    nodesWithLabels.append("circle")
        .attr("r", d => {
            let totalIdCnt = graph[d.id].total_id_cnt;
            return nodeSizeScale(totalIdCnt);
        })
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
        })
        .on("click", function (d) {
            const statusBar = document.getElementById("status-bar");
            statusBar.style.visibility = "visible";

            // Example: Display node information in the status bar
            const statusContent = document.getElementById("status-content");
            statusContent.innerHTML = `
                <div class="status-label">File name: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.id}</div>
            `;
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
        let fileName = d.id.split('/').pop() + " " + graph[d.id].total_id_cnt + " ids";
        const labelWidth = (fileName.length * 8) + 3; // 8px per character plus 6px padding

        // Append a background rectangle for each label
        labelGroup.append("rect")
            .attr("class", "label-bg")
            .attr("rx", 5) // Optional: Adds rounded corners to the background rectangle
            .attr("ry", 5) // Optional: Adds rounded corners to the background rectangle
            .attr("width", labelWidth) // Set the width based on label content and padding
            .attr("height", 20) // Adjust the height of the background rectangle as needed
            .attr("x", -labelWidth / 2) // Adjust the x-coordinate to center the rectangle behind the label
            .attr("y", -10) // Adjust the y-coordinate to center the rectangle behind the label
            .attr("fill", "rgba(0, 0, 0, 0.7)"); // Set the fill color

        // Append the text label inside the label group
        labelGroup.append("text")
            .attr("class", "label-text")
            .attr("data-label-for", d => d.id)
            .text(fileName) // Only the file name
            .attr("dy", 5) // Adjust the vertical position to place the label inside the background rectangle
            .attr("text-anchor", "middle");

        // Initially hide the label group
        labelGroup.style("visibility", "hidden");
    });

    return nodesWithLabels;
}

// ---------------------- INITIALIZE GRAPH ----------------------

d3.json("duplicates-report.json").then(renderGraph);
