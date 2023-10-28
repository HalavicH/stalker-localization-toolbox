import {nodeIsNeighbor, hashCode, dragStarted, dragged, dragEnded} from "/static/misc.js";
import {displayNodeDetails, displayLinkDetails, displayStatistics, copySelfToClipboard, showNotification} from "/static/infoProvider.js"

let multiplier = 1.5


export function renderLinks(svg, links) {
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
            let ids = d.duplicateKeys.join("<br>")
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
                <div class="path">${d.source.id}</div>
                <div class="status-label status-bar-label">Link To: </div>
                <div class="path">${d.target.id}</div>
            `;

            statusContent.addEventListener("click", evt => {
                if (evt.target.classList.contains("path")) {
                    copySelfToClipboard(evt.target);
                }
            });

            displayLinkDetails(d);
        });

}


export function renderNodesWithLabels(svg, nodes, color, force, graph) {
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
                <div class="path">${d.id}</div>
                <div class="status-label status-bar-label">Total ids: </div>
                <div class="path">${d.totalKeysCnt}</div>
            `;

            statusContent.addEventListener("click", evt => {
                if (evt.target.classList.contains("path")) {
                    copySelfToClipboard(evt.target);
                }
            });

            displayNodeDetails(d);
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
