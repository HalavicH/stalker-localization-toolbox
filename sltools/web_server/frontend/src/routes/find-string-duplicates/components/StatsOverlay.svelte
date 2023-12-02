<script>
    import Overlay from "$lib/components/Overlay.svelte";
    import Label from "$lib/components/Label.svelte";
</script>

<style>
    td {
        padding-right: 5px;
    }
</style>

<Overlay style="top: 225px; left: 0;" title="Overall Stats">
    <table>
        <tbody>
        <tr>
            <td class="label">
                <Label text="Nodes (Files):"/>
            </td>
            <td>0</td>
        </tr>
        <tr>
            <td class="label">
                <Label text="Links (Duplicates):"/>
            </td>
            <td>0</td>
        </tr>
        <tr>
            <td class="label">
                <Label text="Total Duplicates:"/>
            </td>
            <td>0</td>
        </tr>
        </tbody>
    </table>
</Overlay>
