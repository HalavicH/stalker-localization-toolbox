<script lang="ts">
    import {onMount} from 'svelte';
    import * as d3 from 'd3';
    import type {ReportData} from "../report";
    import {extractData} from "./render/parser";
    import {status, details, tooltip} from '../store';
    import type {Link, Node} from "../report";
    import {displayLinkDetails, renderNodesWithLabels} from "./render/renderer";
    import type {ScaleOrdinal} from "d3-scale";

    export let report: ReportData;
    export let showAllFiles: boolean;

    // D3 entities
    let svg: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
    let color: ScaleOrdinal<string, unknown>;
    let zoom: any;
    let ret = extractData(report, showAllFiles);
    let links: Link[] = ret.links;
    let nodes: Node[] = ret.nodes;

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

        status.set("Test");
        details.set("details");

        container.call(zoom);
    }

    export function renderGraph() {
        const force = createForceSimulation(800, 600);

        // Create color scale
        color = d3.scaleOrdinal(d3.schemeCategory10);
        console.log(color);

        // Render links within the SVG
        renderLinks();

        // Render nodes with labels within the SVG
        // const nodesWithLabels = renderNodesWithLabels(svg, nodes, color, force);

        // Update positions on simulation "tick"
        force.on("tick", () => {
            svg.selectAll(".link")
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            // Update node and label positions
            // nodesWithLabels.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
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
                const linkData: Link = event.target.__data__;

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

                    displayLinkDetails(link, report);
                }
            );
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