<!-- HTML -->
<div class="tooltip" style={style} id="tooltip">{@html html}</div>

<!-- JS -->
<script lang="ts">
    import {tooltip, type TooltipState} from "$lib/store";

    let html: string;
    let posX: number;
    let posY: number;
    let visibility: string;
    let style: string;

    $: {
        style = `top: ${posY}px; left: ${posX}px; visibility: ${visibility}`;
        console.log("New style: " + style);
    }

    tooltip.subscribe((tooltipState: Partial<TooltipState>) => {
        if (!tooltipState) {
            return;
        }

        if (tooltipState.html) {
            html = tooltipState.html.trim();
        }

        if (tooltipState.posX && tooltipState.posY) {
            posX = tooltipState.posX + 5;
            posY = tooltipState.posY + 5;
        }

        if (tooltipState.visible !== undefined) {
            visibility = tooltipState.visible ? "visible" : "hidden";
        }
    });
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
