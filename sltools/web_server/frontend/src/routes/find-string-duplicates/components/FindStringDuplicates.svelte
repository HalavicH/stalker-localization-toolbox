<script>
    import StatusBar from "./StatusBar.svelte";
    import StatsOverlay from "./StatsOverlay.svelte";
    import LegendOverlay from "./LegendOverlay.svelte";
    import DetailsOverlay from "./DetailsOverlay.svelte";
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
<StatsOverlay/>
<LegendOverlay/>
<DetailsOverlay/>



<StatusBar/>
</body>
