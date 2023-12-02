<!-- HTML -->
<Overlay {style} title="Details">
    {#if (mode === DetailsMode.LinkDetails)}
        <Label>Duplicates in Files:</Label>
        <div class="overlay-data">{getFileName(data.sourceFilePath)}, {getFileName(data.targetFilePath)}</div>
        <StalkerButton id="diff" onClick={handleDiffButton}>Open diff in VS Code</StalkerButton>
        <StalkerButton id="sort" onClick={handleSortButton}>Sort duplicates with sltools</StalkerButton>
        <Row>
            <Label>Total Duplicated IDs:</Label>
            <div class="overlay-data">{data.duplicatedKeysCnt}</div>
        </Row>
        <div class="scrollable-list">
            {@html data.duplicatedKeyDivs.join("\n")}
        </div>
    {:else if (mode === DetailsMode.NodeDetails)}
        <Label>Click on any node/link to see the details</Label>
    {:else}
        <Label>Click on any node/link to see the details</Label>
    {/if}
</Overlay>

<!-- JS -->
<script lang="ts">
    import Label from "$lib/components/Label.svelte";
    import Overlay from "$lib/components/Overlay.svelte";
    import {type DetailsData, details, type LinkDetails, DetailsMode} from "../../store";
    import {getFileName} from "../misc";
    import StalkerButton from "$lib/components/StalkerButton.svelte";
    import {showNotification} from "$lib/js/infoProvider";
    import {openDiffInVsCode, sortEntriesInFiles} from "$lib/js/api";
    import Row from "$lib/components/Row.svelte";

    export let style = ""

    let mode: DetailsMode;
    let data: LinkDetails;

    details.subscribe((newDetails: DetailsData) => {
        console.log("Update details with: ", newDetails);
        if (newDetails) {
            data = newDetails.data;
            mode = newDetails.mode;
        }
    })


    export function handleSortButton() {
        console.log(`Trying to run sort`)

        sortEntriesInFiles(data.sourceFilePath, data.targetFilePath)
            .then(() => {
                console.log(`Sorted entries successfully.`);
                showNotification(`<div>Success!</div>`);
            })
            .catch((error) => {
                console.error(`Error executing command: ${error}`);
            });
    }


    export function handleDiffButton() {
        console.log(`Trying to run diff`)

        openDiffInVsCode(data.sourceFilePath, data.targetFilePath)
            .then(() => {
                console.log(`VS Code diff opened successfully.`);
            })
            .catch((error) => {
                console.error(`Error executing command: ${error}`);
            });
    }
</script>

<!-- CSS -->
<style>
</style>
