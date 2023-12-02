
<!-- Link.svelte -->
<script lang="ts">
    // import type {Link} from '../../report.js';
    export let link: any;
</script>

<line
        class="link"
        x1={link.source.x}
        y1={link.source.y}
        x2={link.target.x}
        y2={link.target.y}
        stroke={link.stroke}
        stroke-width={link.strokeWidth}
/>
