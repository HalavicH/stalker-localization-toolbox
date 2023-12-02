<!-- HTML -->
<div on:click={handleClick} on:keydown={undefined} role="button" tabindex="0">
    <img alt="" {style} src="/common/shutdown.svg">
</div>

<!-- JS -->
<script lang="ts">
    let active = true;
    $: style = active ? "" : "filter: grayscale(1); box-shadow: none;";

    function handleClick() {
        active = !active;
    }
</script>

<!-- CSS -->
<style>
    div {
        position: fixed;
        bottom: 20px;
        left: 0;

        padding: 10px;
        transition: all 0.2s;
    }

    img {
        width: 30px;
        height: 30px;
        border-radius: 50%;

        transition: all 0.2s;
    }

    img:hover {
        box-shadow: 0 0 10px #ff9c5a;
    }
</style>
