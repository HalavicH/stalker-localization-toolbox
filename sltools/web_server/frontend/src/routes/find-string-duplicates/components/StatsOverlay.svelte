<!-- HTML -->
<Overlay {style} title="Overall Stats">
    <table>
        <tbody>
        <tr>
            <td><Label>Nodes (Files):</Label></td>
            <td>0</td>
        </tr>
        <tr>
            <td><Label>Links (Duplicates):</Label></td>
            <td>0</td>
        </tr>
        <tr>
            <td><Label>Total Duplicates:</Label></td>
            <td>0</td>
        </tr>
        </tbody>
    </table>
</Overlay>

<!-- JS -->
<script lang="ts">
    import Overlay from "$lib/components/Overlay.svelte";
    import Label from "$lib/components/Label.svelte";

    export let style = ""
</script>

<!-- CSS -->
<style>
    td {
        padding-right: 5px;
    }
</style>
