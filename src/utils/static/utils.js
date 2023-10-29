import {openDiffInVsCode} from "./backendCommunication.js";

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
