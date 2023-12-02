<script lang="ts">
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
    import type {ReportData} from "../report";
    import {extractData} from "./render/parser";
    import { status, details } from '../store';
    import type {Link, Node} from "../report";
    import {renderLinks, renderNodesWithLabels} from "./render/renderer";

    export let report: ReportData;
    export let showAllFiles: boolean;
    let root: Element;
    let {nodes, links} = extractData(report, showAllFiles);

    // D3 entities
    let svg: d3.Selection<SVGGElement, any, HTMLElement, any>;
    let zoom: any;// d3.ZoomBehavior<Element, any>;

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
        const force = createForceSimulation(nodes, links, 800, 600);

        // Create color scale
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        // Render links within the SVG
        renderLinks(svg, links, report);

        // Render nodes with labels within the SVG
        const nodesWithLabels = renderNodesWithLabels(svg, nodes, color, force);

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

    function createForceSimulation(nodes: Node[], links: Link[], width: number, height: number) {
        return d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links)
                .distance(link => (1 / link.duplicateKeysCnt) * 100 + 100)
                .strength(link => 1 / (link.duplicateKeysCnt + 1)) // Adjust the strength based on duplicate count
            )
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));
    }

</script>

<style>
    #graph-container {
        width: 100%;
        height: 100%;
        overflow: auto;
    }
</style>

<div bind:this={root} id="graph-container"></div>