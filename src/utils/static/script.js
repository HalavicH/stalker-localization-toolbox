// ---------------------- UTILITY FUNCTIONS ----------------------

/**
 * Extract nodes and links from the provided data graph
 * @param {Object} graph
 * @returns {Object} An object containing nodes and links
 */

multiplier = 1.5
show_all_files = false;

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
            msg = hash + " " + overlapInfo.overlapping_ids.sort().join("");

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

function displayStatistics(statistics) {
    const infoOverlay = document.getElementById("overall-stats");
    infoOverlay.innerHTML = `
        <h2>Overall Stats</h2>
        <table>
            <tr>
                <td class="status-label">Total files:</td>
                <td>${statistics.numNodes}</td>
            </tr>
            <tr>
                <td class="status-label">No dups files (grey):</td>
                <td>${statistics.numNoDups}</td>
            </tr>
            <tr>
                <td class="status-label">Files with dups (Blue):</td>
                <td>${statistics.numDups}</td>
            </tr>
            <tr>
                <td class="status-label">Between-files-dups (Links):</td>
                <td>${statistics.numLinks}</td>
            </tr>
            <tr>
                <td class="status-label">Total string duplicates:</td>
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

function calculateDistance(link) {
    // Adjust this calculation based on your data and preferences
    return someBaseDistanceValue + link.numberOfDuplicates * someMultiplier;
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
    const totalDuplicates = links.reduce((total, link) => total + link.duplicateKeysCnt, 0);

    return {numNoDups, numDups, numNodes, numLinks, totalDuplicates};
}

function renderLinks(svg, links) {
    // Render links within the SVG
    const linkElements = svg.selectAll(".link")
        .data(links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke", d => d.color) // Use the color defined in the link
        .attr("stroke-width", d => Math.sqrt(d.duplicateKeysCnt) * multiplier + 1);

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
                <div class="status-label status-bar-label">Link From: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.source.id}</div>
                <div class="status-label status-bar-label">Link To: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.target.id}</div>
            `;

            displayLinkDetails(d);
        });

}

function renderNodesWithLabels(svg, nodes, color, force, graph) {
    // Determine the maximum total_id_cnt to scale the node size
    const maxTotalIdCount = d3.max(nodes, d => d.totalKeysCnt);

    // Create a scale function to map total_id_cnt to node size
    const nodeSizeScale = d3.scaleLinear()
        .domain([0, maxTotalIdCount])
        //  * multiplier
        .range([3, maxTotalIdCount / 10]); // Adjust the range to your desired minimum and maximum node sizes

    const nodesWithLabels = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node");

    // Append a circle for each node with dynamic radius
    nodesWithLabels.append("circle")
        .attr("r", d => {
            let totalIdCnt = d.totalKeysCnt;
            return nodeSizeScale(totalIdCnt);
        })
        .attr("data-node-id", d => d.id)
        .attr("class", "circle")
        .style("fill", d => {
            let folder = d.id.split("/").slice(-2, -1)[0];
            if (d.hasDuplicates) {
                return color(folder);
            } else {
                return "#00000040";
            }
        })
        .call(d3.drag()
            .on("start", d => dragStarted(d, force))
            .on("drag", dragged)
            .on("end", d => dragEnded(d, force))
        )
        .on("mouseover", function (d) {
            let id = `#label-group-${d.index}`;

            // Select the corresponding label group and make it visible
            let element1 = document.querySelector(id);
            element1.style.opacity = "1";
            element1.style.visibility = "visible"
        })
        .on("mouseout", function (d) {
            let id = `#label-group-${d.index}`;

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
                <div class="status-label status-bar-label">File name: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.id}</div>
                <div class="status-label status-bar-label">Total ids: </div>
                <div class="path" onclick="copySelfToClipboard(this)">${d.totalKeysCnt}</div>
            `;
            displayNodeDetails(d, graph);
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
        let fileName = d.id.split('/').pop() + " " + d.totalKeysCnt + " ids";
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

function displayNodeDetails(node, graph) {
    const detailsOverlay = document.getElementById("details");
    detailsOverlay.innerHTML = `
        <h2>Details</h2>
        <div class="legend-item">
            <div class="status-label">File Name: </div>
            <div class="overlay-data">${getFileName(node.id)}</div>
        </div>
            <div class="legend-item">
            <div class="status-label">Total IDs:</div>
            <div class="overlay-data">${node.totalKeysCnt}</div>
        </div>
        <div class="status-label">ID list:</div>
        <div class="scrollable-list">
            ${prepareDivsWithIds(node)}
        </div>
    `;
    detailsOverlay.style.visibility = "visible";
}

function displayLinkDetails(link) {
    const detailsOverlay = document.getElementById("details");
    detailsOverlay.innerHTML = `
        <h2>Details</h2>
        <div class="status-label">Duplicates in Files:</div>
        <div class="overlay-data">${getFileName(link.source.id)}, ${getFileName(link.target.id)}</div>
        <button class="stalker-button" onclick="handleDiffButton(event)" source_file="${link.source.id}" target_file="${link.target.id}">Open diff in VS Code</button>
        <div class="legend-item">
            <div class="status-label">Total Duplicated IDs: </div>
            <div class="overlay-data">${link.duplicateKeysCnt}</div>
        </div>
        <div class="scrollable-list">
            <div class="path">${link.duplicateKeys.join("</div><div class='path' onclick='copySelfToClipboard(this)'>")}</div>
        </div>
    `;
    detailsOverlay.style.visibility = "visible";
}

function getFileName(filePath) {
    const parts = filePath.split("/");
    return parts[parts.length - 1];
}

function prepareDivsWithIds(node) {
    const fileStringIds = node.strings;
    if (fileStringIds && fileStringIds.length > 0) {
        return `<div class="path">${fileStringIds.join("</div><div class='path' onclick='copySelfToClipboard(this)'>")}</div>`;
    } else {
        return "No IDs found. Empty file";
    }
}

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

// ---------------------- INITIALIZE GRAPH ----------------------

//d3.json("visualization_data.json").then(renderGraph);
//data = {{ data_json|safe }}
renderGraph(JSON.parse(globalData))

// Add an event listener to the button
function handleDiffButton(evt) {
    let btn = evt.target;
    // Replace these with the appropriate source and target paths
    const sourcePath = btn.getAttribute("source_file");
    const targetPath = btn.getAttribute("target_file");

    // Execute the shell command to open the diff in VS Code
    console.log(`Trying to run diff`)

    callDiffEndpoint(sourcePath, targetPath)
        .then(() => {
            console.log(`VS Code diff opened successfully.`);
        })
        .catch((error) => {
            console.error(`Error executing command: ${error}`);
        });
}

async function callDiffEndpoint(file1, file2) {
    const url = "http://127.0.0.1:5000/diff";

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({file1, file2})
        });

        const data = await response.json();

        if (response.ok) {
            console.log(data.message);
        } else {
            console.error(data.error);
        }
    } catch (error) {
        console.error("Error calling the endpoint:", error);
    }
}
