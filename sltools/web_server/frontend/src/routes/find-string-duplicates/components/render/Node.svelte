<!-- Node.svelte -->
<script lang="ts">
    // import type {Node} from '../../report.js';
    export let node: any;
</script>

<circle role="button"
        class="node"
        cx={node.x}
        cy={node.y}
        r={node.radius}
        fill={node.fill}
        on:click={() => {
    // Handle click event for nodes here
  }}
        on:focus={() => {
    // Handle mouseover event for nodes here
  }}
        on:blur={() => {
    // Handle mouseout event for nodes here
  }}
/>
