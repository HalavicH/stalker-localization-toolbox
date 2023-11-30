
/**
 * Determines whether two nodes are neighbors
 * @param {Object} nodeA
 * @param {Object} nodeB
 * @returns {boolean}
 */
export function nodeIsNeighbor(nodeA, nodeB, links) {
    return links.some(link =>
        (link.source === nodeA && link.target === nodeB) ||
        (link.source === nodeB && link.target === nodeA)
    );
}

// Function to calculate a hash code for a string
export function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
    }
    return hash;
}

// Show the loading message
export function showLoadingMessage() {
    document.querySelector('.loading-message').style.display = 'block';
}

// Hide the loading message
export function hideLoadingMessage() {
    document.querySelector('.loading-message').style.display = 'none';
}

// ---------------------- DRAG HANDLERS ----------------------

export function dragStarted(d, force) {
    if (!d3.event.active) force.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

export function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

export function dragEnded(d, force) {
    if (!d3.event.active) force.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

export function downloadObjectAsJson(obj, filename) {
    let jsonString = JSON.stringify(obj, null, 4);
    let blob = new Blob([jsonString], {type: "application/json"});
    let link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}