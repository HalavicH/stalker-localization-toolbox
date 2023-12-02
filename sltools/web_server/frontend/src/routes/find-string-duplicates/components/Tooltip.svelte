<!-- HTML -->
{#if (data.length)}
    <div class="tooltip" id="tooltip">{@html data}</div>
{/if}

<!-- JS -->
<script lang="ts">
    import {tooltipData} from "../store";

    let data: string;
    tooltipData.subscribe((html: string) => {
        console.log("Update tooltip with: ", html);
        data = html.trim();
    })
</script>

<!-- CSS -->
<style>
    .tooltip {
        position: absolute;
        visibility: hidden;
        background-color: rgba(0, 0, 0, 0.3); /* Bluish-grayish-darkish background */
        backdrop-filter: blur(5px); /* Apply the blur effect */
        color: #dcdcdc; /* Light gray text */
        padding: 5px;
        border-radius: 5px;
    }
</style>
