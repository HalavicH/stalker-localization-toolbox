<!-- HTML -->
<div class="overlay" id="overall-stats" {style} on:click={handleClick} on:keydown={undefined} role="button" tabindex="0">
    <h2>{title}</h2>
    <slot></slot>
</div>

<!-- JS -->
<script lang="ts">
    import {copyTextToClipboard} from "../misc";

    export let style: string;
    export let title: string = "";


    function handleClick(evt: Event) {
        const t = evt.target as HTMLDivElement;
        if (!t) {
            return;
        }

        if (t.classList.contains("path")) {
            copyTextToClipboard(t.innerText);
        }
    }
</script>

<!-- CSS -->
<style>
    /* Overlay */
    .overlay {
        position: fixed;
        background-color: rgba(30, 30, 30, 0.3);
        backdrop-filter: blur(5px);
        color: #dcdcdc;
        border: 2px solid #202020;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        transition: box-shadow 0.2s ease-in-out;
        padding: 20px 10px 10px 20px;
        margin: 8px 5px;
        max-width: 30%;
        max-height: 50%;
        z-index: 999;
        overflow: auto;
    }

    .overlay:hover {
        box-shadow: 0 0 10px rgba(255, 156, 90, 0.3);
    }

    h2 {
        color: #ff9c5a;
        margin-top: 10px;
    }

</style>
