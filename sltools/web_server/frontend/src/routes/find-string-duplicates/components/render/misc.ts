
/**
 * Determines whether two nodes are neighbors
 * @param {Object} nodeA
 * @param {Object} nodeB
 * @returns {boolean}
 */
export function nodeIsNeighbor(nodeA: any, nodeB: any, links: any) {
    return links.some((link: any) =>
        (link.source === nodeA && link.target === nodeB) ||
        (link.source === nodeB && link.target === nodeA)
    );
}

// Function to calculate a hash code for a string
export function hashCode(str: string) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
    }
    return hash;
}


// ---------------------- DRAG HANDLERS ----------------------

export function dragStarted(d: any, force: any) {
    if (!d3.event.active) force.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

export function dragged(d: any) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

export function dragEnded(d: any, force: any) {
    if (!d3.event.active) force.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

export function downloadObjectAsJson(obj: any, filename: any) {
    const jsonString: string = JSON.stringify(obj, null, 4);
    const blob = new Blob([jsonString], {type: "application/json"});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}