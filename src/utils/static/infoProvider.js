import {getFileName, prepareDivsWithIds, handleDiffButton} from "/static/utils.js";
import {nodeIsNeighbor, hashCode, dragStarted, dragged, dragEnded} from "/static/misc.js";
import {renderLinks, renderNodesWithLabels} from "/static/renderer.js"


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

export function displayLinkDetails(link) {
    const detailsOverlay = document.getElementById("details");
    detailsOverlay.innerHTML = `
        <h2>Details</h2>
        <div class="status-label">Duplicates in Files:</div>
        <div class="overlay-data">${getFileName(link.source.id)}, ${getFileName(link.target.id)}</div>
        <button class="stalker-button" source_file="${link.source.id}" target_file="${link.target.id}">Open diff in VS Code</button>
        <div class="legend-item">
            <div class="status-label">Total Duplicated IDs: </div>
            <div class="overlay-data">${link.duplicateKeysCnt}</div>
        </div>
        <div class="scrollable-list">
            <div class="path">${link.duplicateKeys.join("</div><div class='path' onclick='copySelfToClipboard(this)'>")}</div>
        </div>
    `;
    detailsOverlay.querySelector(".stalker-button").addEventListener("click", handleDiffButton);
    detailsOverlay.style.visibility = "visible";
}

export function displayStatistics(statistics) {
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

// Function to show a notification in the top right corner
export function showNotification(html) {
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