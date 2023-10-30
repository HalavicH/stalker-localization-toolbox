import {getFileName, prepareDivsWithIds, handleDiffButton, handleSortButton} from "./utils.js";
import {downloadObjectAsJson} from "./misc.js";


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

export function displayLinkDetails(link, graph) {
    const detailsOverlay = document.getElementById("details");
    let duplicatesDivs = [];

    link.duplicateKeys.forEach(dup => {
        let hash1 = graph.file_to_string_mapping[link.source.id][dup];
        let hash2 = graph.file_to_string_mapping[link.target.id][dup];
    
        console.log("hash1 " + hash1 + " hash2" + hash2);
        if (hash1 === hash2) {
            duplicatesDivs.push(`<div class="path same-content">${dup}</div>`);
        } else {
            duplicatesDivs.push(`<div class="path">${dup}</div>`);
        }
    })

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
    })

    detailsOverlay.innerHTML = `
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
    `;

    detailsOverlay.querySelector("#diff").addEventListener("click", handleDiffButton);
    detailsOverlay.querySelector("#sort").addEventListener("click", handleSortButton);

    detailsOverlay.addEventListener("click", evt => {
        if (evt.target.classList.contains("path")) {
            copySelfToClipboard(evt.target);
        }
    });

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
            <tr>
                <td class="status-label">Total uniq string IDs:</td>
                <td>${statistics.uniqStrings.size}</td>
                <td id="download-unique-strings" class="downloadable has-tooltip">
                    <div class="download-icon-container">
                        <img src="/static/download.svg" class="download-icon" alt=""/>
                        <div class="tooltiptext">Download all unique strings as JSON file<div/>
                    </div>
                </td>
            </tr>
        </table>
    `;

    // Setup downloads
    infoOverlay.querySelector("#download-unique-strings").addEventListener("click", () => {
        downloadObjectAsJson(Array.from(statistics.uniqStrings).sort(), "unique-strings-all-files.json");
    });
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
    const className = "notification";
    showBanner(html, className);
}

// Function to show a notification in the top right corner
export function showError(html) {
    const className = "error-banner";
    showBanner(html, className);
}

function showBanner(html, className) {
    const notification = document.createElement("div");
    notification.innerHTML = html;
    notification.className = className;

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

