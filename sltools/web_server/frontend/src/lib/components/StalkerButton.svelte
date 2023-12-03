<!-- HTML -->
<button id={id} on:click={onClick}>
    <slot></slot>
</button>

<!-- JS -->
<script lang="ts">
    export let id: string;
    export let onClick: any;
</script>

<!-- CSS -->
<style>
    /* STALKER button */
    button {
        background-color: #444;
        border: 2px solid #777;
        color: #eee;
        font-family: 'Arial', sans-serif; /* You can replace this with a more rugged font if you have one */
        font-size: 12px;
        padding: 5px 10px;
        margin: 5px 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        cursor: pointer;
        /*transition: all 0.3s ease-in;*/
        text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.7);
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
        border-radius: 5px;
        outline: none;
    }

    button:hover {
        background-color: #555;
        border-color: #888;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.7);
    }

    button:active {
        background-color: #333;
        border-color: #666;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8);
        transform: scale(0.98);
    }
</style>
