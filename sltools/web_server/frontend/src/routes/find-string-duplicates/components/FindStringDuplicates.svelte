<!-- HTML -->
<body>
<!-- D3 graph -->
{#if (!loaded)}
    <PageSpinner/>
{:else}
    <GraphView {report} {showAllFiles}/>
{/if}

<!-- Overlays -->
<LegendOverlay style="top: 0; left: 0;" on:height={handleLegendHeight}/>
<StatsOverlay style="top: {legendHeight}px; left: 0;"/>
<DetailsOverlay style="top: 0; right: 0; width: 25%; max-height: 91%;"/>

<!-- Misc -->
<Shutdown/>
<StatusBar/>
<Tooltip/>
</body>

<!-- JS -->
<script lang="ts">
    import StatusBar from "./StatusBar.svelte";
    import StatsOverlay from "./overlays/StatsOverlay.svelte";
    import LegendOverlay from "./overlays/LegendOverlay.svelte";
    import DetailsOverlay from "./overlays/DetailsOverlay.svelte";
    import PageSpinner from "$lib/components/PageSpinner.svelte";
    import Shutdown from "$lib/components/Shutdown.svelte";
    import GraphView from "./GraphView.svelte";
    import _report from "../report.json"
    import type {ReportData} from "$lib/report";
    import Tooltip from "./Tooltip.svelte";
    import {storeShowAllFiles} from "$lib/store";

    let legendHeight = -250;
    let loaded = false;

    let report: ReportData;
    let showAllFiles: boolean;

    setInterval(() => {
        report = _report;
        loaded = true;
    }, 100)

    function handleLegendHeight(e: CustomEvent) {
        legendHeight = e.detail;
    }

    storeShowAllFiles.subscribe((newValue: boolean) => {
        console.log("Got update for show all files: " + newValue);
        showAllFiles = newValue;
    });
</script>

<!-- CSS -->
<style>
    body {
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: #282c34; /* Obsidian background color */
    }
</style>
