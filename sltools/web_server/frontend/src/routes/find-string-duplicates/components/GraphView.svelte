<script lang="ts">
    import {onMount} from 'svelte';
    import * as d3 from 'd3';
    import type {D3Link, Node, ReportData, ReportLink} from "$lib/report";
    import {details, type DetailsData, DetailsMode, status, tooltip} from '$lib/store';
    import type {ScaleOrdinal} from "d3-scale";
    import type {NumberValue, SimulationNodeDatum} from "d3";

    export let report: ReportData;
    export let showAllFiles: boolean;

    // D3 entities
    let svg: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
    let color: ScaleOrdinal<string, unknown>;
    let zoom: any;
    let ret = extractData(report, showAllFiles);
    let links: ReportLink[] = ret.links;
    let nodes: Node[] = ret.nodes;
    let force: any;

    console.log("Loading Graphview!");

    onMount(() => {
        console.log("Run graph render");
        createZoomableSVG();
        renderGraph();
    });

    function createZoomableSVG() {
        const container = d3.select('#graph-container');

        svg = container
            .append('svg')
            .attr('width', '100vw')
            .attr('height', '100vh')
            .append('g');

        zoom = d3.zoom()
            .scaleExtent([0.1, 10]) // Adjust the zoom scale extent as needed
            .on('zoom', (event) => { // Use the 'event' parameter to access the zoom event
                svg.attr('transform', event.transform);
            });

        container.call(zoom);
    }

    export function renderGraph() {
        force = createForceSimulation(800, 600);

        color = d3.scaleOrdinal(d3.schemeCategory10);
        console.log(color);

        renderLinks();
        const nodesWithLabels = renderNodesWithLabels();

        // Update positions on simulation "tick"
        force.on("tick", () => {
            svg.selectAll(".link")
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            // Update node and label positions
            nodesWithLabels.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
        });

        // let stats = calculateStats(links, nodes);
        // displayStatistics(stats);
    }

    function createForceSimulation(width: number, height: number) {
        return d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links)
                .distance(link => (1 / link.duplicateKeysCnt) * 100 + 100)
                .strength(link => 1 / (link.duplicateKeysCnt + 1)) // Adjust the strength based on duplicate count
            )
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));
    }

    export function renderLinks() {
        // Render links within the SVG
        const multiplier = 1;
        const linkElements = svg.selectAll(".link")
            .data(links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke", d => d.color) // Use the color defined in the link
            .attr("stroke-width", d => Math.sqrt(d.duplicateKeysCnt) * multiplier + 1);

        // Add a tooltip to show the number of duplicate keys when hovering over the link
        linkElements
            .on("mouseover", function (event: any) {
                const linkData: ReportLink = event.target.__data__;

                const header = `Duplicate Keys: (Total: ${linkData.duplicateKeysCnt})<br>`;
                const ids = linkData.duplicateKeys.join("<br>")
                tooltip.set({
                    html: (header + ids),
                    visible: true
                });
            })
            .on("mousemove", function (event: any) {
                let top = (event.pageY);
                let left = (event.pageX);
                tooltip.set({posX: left, posY: top});
            })
            .on("mouseout", function () {
                tooltip.set({visible: false});
            })
            .on("click", function (event: any) {
                    const link: any = event.target.__data__;

                    let html = `
                        <div class="status-label status-bar-label">Link From: </div>
                        <div class="path">${link.source.id}</div>
                        <div class="status-label status-bar-label">Link To: </div>
                        <div class="path">${link.target.id}</div>
                    `;
                    status.set(html);

                    displayLinkDetails(link);
                }
            );
    }

    export function displayLinkDetails(link: D3Link) {
        let duplicatesDivs: string[] = [];

        link.duplicateKeys.forEach((dup: string) => {
            let hash1 = report.file_to_string_mapping[link.source.id][dup];
            let hash2 = report.file_to_string_mapping[link.target.id][dup];

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
        let newDetails: DetailsData = {
            mode: DetailsMode.LinkDetails,
            data: {
                sourceFilePath: link.source.id,
                targetFilePath: link.target.id,
                duplicatedKeysCnt: link.duplicateKeys.length,
                duplicatedKeyDivs: duplicatesDivs,
            }
        }
        details.set(newDetails);
    }

    // Drag handlers
    // Define your drag handlers as functions
    function dragStarted(event: any, d: any, force: any) {
        if (!event.active) force.alphaTarget(0.3).restart();
        d.fx = d.x || 0;
        d.fy = d.y || 0;
    }

    function dragged(event: any, d: any) {
        d.fx = event.x || 0;
        d.fy = event.y || 0;
    }

    function dragEnded(event: any, d: any, force: any) {
        if (!event.active) force.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    export function renderNodesWithLabels() {
        const maxIdsInSingleFile = d3.max(nodes, node => node.totalKeysCnt) || 0;

        // Create a scale function to map total_id_cnt to node size
        const nodeSizeScale = d3.scaleLinear()
            .domain([0, maxIdsInSingleFile] as Iterable<NumberValue>)
            .range([3, maxIdsInSingleFile / 10] as Iterable<number>);

        const nodesWithLabels = svg.selectAll(".node")
            .data(nodes)
            .enter()
            .append("g")
            .attr("class", "node");

        // Append a circle for each node with dynamic radius
        let drag = d3.drag<SVGCircleElement, SimulationNodeDatum>()
            .on("start", (event, d) => dragStarted(event, d, force))
            .on("drag", dragged)
            .on("end", (event, d) => dragEnded(event, d, force));

        nodesWithLabels.append("circle")
            .attr("r", d => {
                let totalIdCnt = d.totalKeysCnt;
                return nodeSizeScale(totalIdCnt);
            })
            .attr("data-node-id", node => node.id)
            .attr("class", "circle")
            .style("fill", "#00000040")
            .call(drag as any)
            .on("mouseover", function (event: any) {
                const node: any = event.target.__data__;

                tooltip.set({
                    html: (`"File: ${node.id}`),
                    visible: true
                });
            })
            .on("mousemove", function (event: any) {
                let top = (event.pageY);
                let left = (event.pageX);
                tooltip.set({posX: left, posY: top});
            })
            .on("mouseout", function () {
                tooltip.set({visible: false});
            })
            .on("click", function (event) {
                const node: any = event.target.__data__;
                status.set(`
                <div class="status-label status-bar-label">File name: </div>
                <div class="path">${node.id}</div>
                <div class="status-label status-bar-label">Total ids: </div>
                <div class="path">${node.totalKeysCnt}</div>
            `);

                displayNodeDetails(node);
            });

        return nodesWithLabels;
    }

    export function displayNodeDetails(node: Node) {
        function prepareDivsWithIds(node: Node) {
            const fileStringIds = node.strings;
            if (fileStringIds && fileStringIds.length > 0) {
                return `<div class="path">${fileStringIds.join("</div><div class='path''>")}</div>`;
            } else {
                return "No IDs found. Empty file";
            }
        }

        let newDetails: DetailsData = {
            mode: DetailsMode.NodeDetails,
            data: {
                filePath: node.id,
                keysCnt: node.totalKeysCnt,
                allKeysAsDivList: prepareDivsWithIds(node),
            }
        }
        details.set(newDetails);
    }

    export function extractData(report: ReportData, showAllFiles: boolean): {nodes: Node[], links: ReportLink[]} {
        const { nodes, nodeMap } = createNodesArray(report, showAllFiles);
        const links: ReportLink[] = [];

        for (const file in report.overlaps_report) {
            const sourceIndex = nodeMap[file];
            for (const overlapFile in report.overlaps_report[file].overlaps) {
                const targetIndex = nodeMap[overlapFile];
                const overlapInfo = report.overlaps_report[file].overlaps[overlapFile];
                const sortedOverlappingIds = overlapInfo.overlapping_ids.sort();
                const hash = Math.abs(hashCode(sortedOverlappingIds.join('')));
                links.push({
                    source: sourceIndex,
                    target: targetIndex,
                    duplicateKeysCnt: overlapInfo.match_count,
                    duplicateKeys: sortedOverlappingIds,
                    color: d3.schemeCategory10[hash % 10],
                });
            }
        }

        return { nodes, links };
    }

    function createNodesArray(report: ReportData, showAllFiles: boolean) {
        const nodes: Node[] = [];
        const nodeMap: Record<string, number> = {};
        let index = 0;

        for (const file in report.file_to_string_mapping) {
            const hasDuplicates = !!report.overlaps_report[file];
            if (!showAllFiles && !hasDuplicates) {
                continue;
            }

            const strings = Object.keys(report.file_to_string_mapping[file]);
            nodes.push({
                id: file,
                strings: strings,
                index: index,
                totalKeysCnt: strings.length,
                hasDuplicates: hasDuplicates,
            });

            nodeMap[file] = index;
            index++;
        }

        return { nodes, nodeMap };
    }

    export function hashCode(str: string) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
        }
        return hash;
    }

</script>

<style>
    #graph-container {
        width: 100%;
        height: 100%;
        overflow: auto;
    }
</style>

<div id="graph-container"></div>