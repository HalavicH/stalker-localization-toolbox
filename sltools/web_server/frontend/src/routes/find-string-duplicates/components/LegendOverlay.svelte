<script lang="ts">
    import Overlay from "$lib/components/Overlay.svelte";
    import Row from "$lib/components/Row.svelte";
    import Label from "$lib/components/Label.svelte";
    import { createEventDispatcher, onMount, onDestroy } from "svelte";

    // Props
    export let style = "";

    let yes = false;
    $: showAllNodes = "display: " + (yes ? "block" : "none");

    // Dynamic height
    let ref: HTMLDivElement;
    let height: number;
    const dispatch = createEventDispatcher();
    let resizeObserver;

    function updateHeight() {
        if (ref) {
            let parentElement = ref.parentElement;
            height = parentElement ? (parentElement.clientHeight + 8) : 0;
            dispatch("height", height);
        }
    }

    // Get the height of the table element and emit it to the parent component on mount
    onMount(() => {
        updateHeight();
        resizeObserver = new ResizeObserver(updateHeight);
        resizeObserver.observe(ref);
    });

    // Update the height when the component is about to update
    onDestroy(() => {
        // Clean up the ResizeObserver when the component is destroyed
        if (resizeObserver) {
            resizeObserver.disconnect();
        }
    });
</script>

<style>
    svg {
        width: 25px;
        height: 20px;
    }
</style>

<Overlay {style} title="Legend">
    <div bind:this={ref}> <!-- get the height of the component -->
        <Row>
            <svg>
                <g class="node" transform="translate(12.5,10)">
                    <circle class="circle" r="7" style="fill: rgb(31, 119, 180);"></circle>
                </g>
            </svg>
            <Label>&nbsp;- Nodes (Files)</Label>
        </Row>
        <Row>
            <!-- Link line here -->
            <svg>
                <line class="link" stroke-width="7.615773105863909" style="stroke: rgb(148, 103, 189);"
                      x1="3.9668105921197"
                      x2="20.28503239344536" y1="5.94242643288266" y2="15.03946082603545"></line>
            </svg>
            <Label>&nbsp;- Links (Duplicates)</Label>
        </Row>
        <Row>
            <Label>Link color - uniq set of duplicates</Label>
        </Row>
        <Row>
            <Label>
                <input id="show-all-files" type="checkbox" bind:checked={yes}/>
                Show all files (even without dups)
            </Label>
        </Row>
        <Row style={showAllNodes}>
            <svg>
                <g class="node" transform="translate(12.5,10)">
                    <circle class="circle" r="7" style="fill: rgba(0,0,0,0.35);"></circle>
                </g>
            </svg>
            <Label>&nbsp;- No-dup files</Label>
        </Row>
    </div>
</Overlay>
