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

    callDiffEndpoint(sourcePath, targetPath)
        .then(() => {
            console.log(`VS Code diff opened successfully.`);
        })
        .catch((error) => {
            console.error(`Error executing command: ${error}`);
        });
}

export async function callDiffEndpoint(file1, file2) {
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
