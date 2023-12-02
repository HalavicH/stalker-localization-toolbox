<!-- HTML -->
<div class="status-bar" id="status-bar" on:click={handleClick} on:keydown={undefined} role="button" tabindex="0">
    <div id="status-content">
        {@html data}
    </div>
</div>

<!-- JS -->
<script lang="ts">
    import {status} from "$lib/store.js";
    import {copyTextToClipboard} from "$lib/misc";

    let data: string;
    status.subscribe((newStatus) => {
        console.log("Update statusbar with: ", newStatus);
        data = newStatus;
    });

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
    /* Status Bar */
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.3); /* Bluish-grayish-darkish background */
        backdrop-filter: blur(5px); /* Apply the blur effect */
        color: #dcdcdc; /* Light gray text */
        box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.2); /* Shadow at the bottom */
        padding: 3px 5px;
        z-index: 1000;
    }

    #status-content {
        display: flex;
        flex-direction: row;
    }

    :global(.status-bar-label) {
        margin: 0 5px 0 5px;
    }

    :global(.path) {
        font-family: monospace;
        color: #ff9c5a;
        cursor: pointer;
    }

</style>
