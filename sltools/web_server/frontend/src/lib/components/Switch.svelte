<script lang="ts">
    export let checked = false;
    const uniqueID = Math.floor(Math.random() * 100)

    function handleClick(event: any){
        const target = event.target

        const state = target.getAttribute('aria-checked')

        checked = state === 'true' ? false : true
    }
</script>

<div>
    <button
            role="switch"
            aria-checked={checked}
            aria-labelledby={`switch-${uniqueID}`}
            on:click={handleClick}>
    </button>
</div>

<style>
    :root {
        --accent-color: #ff9c5a;
        --gray: #5f7796;
    }

    /* Slider Design Option */

    div {
        display: flex;
        align-items: center;
        padding: 0.1em;
    }

    button {
        width: 2.5em;
        height: 1.35em;
        position: relative;
        margin: 0 0.5em 0 0;
        background: var(--gray);
        border: none;
    }

    button::before {
        content: '';
        position: absolute;
        width: 1.1em;
        height: 1.1em;
        background: rgba(255, 255, 255, 0.73);
        top: 0.125em;
        right: 1.25em;
        transition: transform 0.3s;
    }

    button[aria-checked='true'] {
        background-color: var(--accent-color)
    }

    button[aria-checked='true']::before{
        transform: translateX(1.1em);
        transition: transform 0.3s;
    }

    button:focus {
        box-shadow: 0 0 0px 1px var(--accent-color);
    }

    /* Slider Design Option */
    button {
        border-radius: 1.5em;
    }

    button::before {
        border-radius: 100%;
    }

    button:focus {
        box-shadow: 0 0px 8px var(--accent-color);
        border-radius: 1.5em;
    }


</style>