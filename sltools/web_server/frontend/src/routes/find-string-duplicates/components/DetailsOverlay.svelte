<script>
    import Overlay from "$lib/components/Overlay.svelte";
    import Label from "$lib/components/Label.svelte";

    export let style = ""
</script>

<style>
</style>

<Overlay {style} title="Details">
    <Label>Click on any node/link to see the details</Label>
</Overlay>
