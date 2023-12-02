<script>
    import Overlay from "$lib/components/Overlay.svelte";
</script>

<style>
    .label {
        font-weight: bold;
        color: #999999;
    }
</style>

<Overlay style="top: 225px; left: 0;" title="Overall Stats">
    <table>
        <tbody>
        <tr>
            <td class="label">Nodes (Files):</td>
            <td>0</td>
        </tr>
        <tr>
            <td class="label">Links (Duplicates):</td>
            <td>0</td>
        </tr>
        <tr>
            <td class="label">Total Duplicates:</td>
            <td>0</td>
        </tr>
        </tbody>
    </table>
</Overlay>
