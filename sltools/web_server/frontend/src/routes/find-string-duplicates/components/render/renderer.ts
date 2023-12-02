import * as d3 from "d3";
import type {ReportData, Node, Link} from "../../report";
import {dragEnded, dragged, dragStarted} from "./misc";


export function getFileName(filePath: string) {
    const parts = filePath.split("/");
    return parts[parts.length - 1];
}

export function prepareDivsWithIds(node: any) {
    const fileStringIds = node.strings;
    if (fileStringIds && fileStringIds.length > 0) {
        return `<div class="path">${fileStringIds.join("</div><div class='path''>")}</div>`;
    } else {
        return "No IDs found. Empty file";
    }
}

export function renderNodesWithLabels(svg: any, nodes: Node[], color: any, force: any) {
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
            const id = `#label-group-${d.index}`;

            // Select the corresponding label group and make it visible
            const element1: HTMLDivElement | null = document.querySelector(id);
            if (element1) {
                element1.style.opacity = "1";
                element1.style.visibility = "visible"
            }
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

export function displayLinkDetails(link: Link, graph: GraphData) {
    let duplicatesDivs: string[] = [];

    link.duplicateKeys.forEach((dup) => {
        let hash1 = graph.file_to_string_mapping[link.source.id][dup];
        let hash2 = graph.file_to_string_mapping[link.target.id][dup];

        console.log("hash1 " + hash1 + " hash2" + hash2);
        if (hash1 === hash2) {
            duplicatesDivs.push(`<div class="path same-content">${dup}</div>`);
        } else {
            duplicatesDivs.push(`<div class="path">${dup}</div>`);
        }
    });

    duplicatesDivs.sort((a, b) => {
        if (a.includes("same-content")) {
            if (b.includes("same-content")) {
                return 0;
            }
            return -1;
        }
        if (!b.includes("same-content")) {
            return 1;
        }
        return 0;
    });

    // Construct the details content using Svelte store
    $details.set(`
    <h2>Details</h2>
    <div class="status-label">Duplicates in Files:</div>
    <div class="overlay-data">${getFileName(link.source.id)}, ${getFileName(link.target.id)}</div>
    <button id="diff" class="stalker-button" source_file="${link.source.id}" target_file="${link.target.id}">Open diff in VS Code</button>
    <button id="sort" class="stalker-button" source_file="${link.source.id}" target_file="${link.target.id}">Sort duplicates with sltools</button>
    <div class="legend-item">
        <div class="status-label">Total Duplicated IDs: </div>
        <div class="overlay-data">${link.duplicateKeysCnt}</div>
    </div>
    <div class="scrollable-list">
        ${duplicatesDivs.join("\n")}
    </div>
  `);

    // Attach event listeners using Svelte store
    const handleDiffButton = () => {
        // Your logic for handling the "Open diff in VS Code" button
    };

    const handleSortButton = () => {
        // Your logic for handling the "Sort duplicates with sltools" button
    };

    const copySelfToClipboard = (target: EventTarget) => {
        // Your logic for copying to clipboard
    };

    const detailsOverlay = document.getElementById("details");

    // Attach event listeners using Svelte store
    detailsOverlay.querySelector("#diff").addEventListener("click", handleDiffButton);
    detailsOverlay.querySelector("#sort").addEventListener("click", handleSortButton);

    detailsOverlay.addEventListener("click", (evt) => {
        if (evt.target.classList.contains("path")) {
            copySelfToClipboard(evt.target);
        }
    });

    // Set visibility using Svelte store
    detailsOverlay.style.visibility = "visible";
}


export function copySelfToClipboard(element) {
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


export function displayNodeDetails(node) {
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

    detailsOverlay.addEventListener("click", evt => {
        if (evt.target.classList.contains("path")) {
            copySelfToClipboard(evt.target);
        }
    });


    detailsOverlay.style.visibility = "visible";
}

export function showNotification(html: any) {
    const className = "notification";
    // showBanner(html, className);
}
