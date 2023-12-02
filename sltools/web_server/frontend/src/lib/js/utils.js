import {executePostRequest, openDiffInVsCode, sortEntriesInFiles} from "./api.js";
import {showNotification} from "./infoProvider.js";

export function getFileName(filePath) {
    const parts = filePath.split("/");
    return parts[parts.length - 1];
}

export function prepareDivsWithIds(node) {
    const fileStringIds = node.strings;
    if (fileStringIds && fileStringIds.length > 0) {
        return `<div class="path">${fileStringIds.join("</div><div class='path''>")}</div>`;
    } else {
        return "No IDs found. Empty file";
    }
}

export function handleSortButton(evt) {
    let btn = evt.target;
    // Replace these with the appropriate source and target paths
    const sourcePath = btn.getAttribute("source_file");
    const targetPath = btn.getAttribute("target_file");

    // Execute the shell command to open the diff in VS Code
    console.log(`Trying to run sort`)

    sortEntriesInFiles(sourcePath, targetPath)
        .then(() => {
            console.log(`Sorted entries successfully.`);
            showNotification(`<div>Success!</div>`);
        })
        .catch((error) => {
            console.error(`Error executing command: ${error}`);
        });
}


// Add an event listener to the button
export function handleDiffButton(evt) {
    let btn = evt.target;
    // Replace these with the appropriate source and target paths
    const sourcePath = btn.getAttribute("source_file");
    const targetPath = btn.getAttribute("target_file");

    // Execute the shell command to open the diff in VS Code
    console.log(`Trying to run diff`)

    openDiffInVsCode(sourcePath, targetPath)
        .then(() => {
            console.log(`VS Code diff opened successfully.`);
        })
        .catch((error) => {
            console.error(`Error executing command: ${error}`);
        });
}

export function handlePowerButton(evt) {
    console.log("Try to shutdown the server");
    executePostRequest("/shutdown", 0)
        .then(() => {
            document.querySelector(".shutdown-container").classList.add("inactive");
            showNotification("Stopped server");
        })
        .catch((error) => {
            showNotification("Server already shut down");

        });
}