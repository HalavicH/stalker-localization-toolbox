<!-- HTML -->
<body>
<!-- D3 graph -->
<GraphView/>

<!-- Overlays -->
<LegendOverlay style="top: 0; left: 0;" on:height={handleLegendHeight}/>
<StatsOverlay style="top: {legendHeight}px; left: 0;"/>
<DetailsOverlay style="top: 0; right: 0; width: 25%; max-height: 91%;"/>

<!-- Misc -->
<PageSpinner/>
<Shutdown/>
<StatusBar/>
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

    let legendHeight = -250;

    function handleLegendHeight(e: CustomEvent) {
        legendHeight = e.detail
    }
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
