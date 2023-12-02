<script lang="ts">
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
    import type {ReportData} from "../report";
    import {extractData} from "./render/parser";

    export let report: ReportData;
    export let showAllFiles: boolean;
    let root: Element;
    let {nodes, links} = extractData(report, showAllFiles);

    // D3 entities
    let svg: d3.Selection<SVGGElement, any, HTMLElement, any>;
    let zoom: d3.ZoomBehavior<Element, any>;

    onMount(() => {
        createZoomableSVG();
    });

    function createZoomableSVG() {
        const container = d3.select('#graph-container');

        svg = container
            .append('svg')
            .attr('width', '100vh')
            .attr('height', '100vh')
            .append('g');

        zoom = d3
            .zoom()
            .scaleExtent([0.1, 10]) // Adjust the zoom scale extent as needed
            .on('zoom', () => {
                svg.attr('transform', d3.event.transform);
            });

        container.call(zoom);
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