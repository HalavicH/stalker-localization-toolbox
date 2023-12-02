<!-- HTML -->
<Overlay {style} title="Details">
    <Label>{@html data}</Label>
</Overlay>

<!-- JS -->
<script lang="ts">
    import Overlay from "$lib/components/Overlay.svelte";
    import Label from "$lib/components/Label.svelte";
    import {details} from "../../store";

    export let style = ""

    let data: string;
    details.subscribe(newDetails => {
        console.log("Update details with: ", newDetails);
        data = newDetails;
    })
</script>

<!-- CSS -->
<style>
</style>
