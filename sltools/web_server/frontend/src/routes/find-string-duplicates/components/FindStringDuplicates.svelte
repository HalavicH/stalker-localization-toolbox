<script lang="ts">
    import StatusBar from "./StatusBar.svelte";
    import StatsOverlay from "./StatsOverlay.svelte";
    import LegendOverlay from "./LegendOverlay.svelte";
    import DetailsOverlay from "./DetailsOverlay.svelte";
    import PageSpinner from "$lib/components/PageSpinner.svelte";
    import Shutdown from "$lib/components/Shutdown.svelte";

    let legendHeight = -250;

    function handleLegendHeight(e: CustomEvent) {
        legendHeight = e.detail
    }
</script>

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

<body>
<LegendOverlay style="top: 0; left: 0;" on:height={handleLegendHeight}/>
<StatsOverlay style="top: {legendHeight}px; left: 0;"/>
<DetailsOverlay style="top: 0; right: 0; width: 25%; max-height: 91%;"/>
<PageSpinner/>
<Shutdown/>
<StatusBar/>
</body>
