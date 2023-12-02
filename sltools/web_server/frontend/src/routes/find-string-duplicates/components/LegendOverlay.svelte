<script>
    import Overlay from "$lib/components/Overlay.svelte";
    import Row from "$lib/components/Row.svelte";
</script>

<style>
    .status-label {
        font-weight: bold;
        color: #999999;
    }

    /*    */
    /* Legend */
    .legend-circle {
        width: 20px;
        height: 20px;
        background-color: rgb(31, 119, 180);
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }

    .legend-item {
        display: flex;
        flex-direction: row;
        vertical-align: center;
    }

    /*    */
    #svg-legend {
        width: 25px;
        height: 20px;
    }

    /*#details {*/
    /*    top: 0;*/
    /*    right: 0;*/
    /*    width: 25%;*/
    /*    max-height: 91%;*/
    /*}*/

</style>

<Overlay style="top: 0; left: 0;" title="Legend">
    <Row>
        <svg id="svg-legend">
            <g class="node" transform="translate(12.5,10)">
                <circle class="circle" r="7" style="fill: rgb(31, 119, 180);"></circle>
            </g>
        </svg>
        <div class="legend-label">&nbsp;- Nodes (Files)</div>
    </Row>
    <Row>
        <!-- Link line here -->
        <svg id="svg-legend">
            <line class="link" stroke-width="7.615773105863909" style="stroke: rgb(148, 103, 189);" x1="3.9668105921197"
                  x2="20.28503239344536" y1="5.94242643288266" y2="15.03946082603545"></line>
        </svg>
        <div class="legend-label">&nbsp;- Links (Duplicates)</div>
    </Row>
    <Row>
        <div class="legend-label">Link color - uniq set of duplicates</div>
    </Row>
    <Row>
        <label>
            <input id="show-all-files" type="checkbox"/>
            Show all files (even without dups)
        </label>
    </Row>
    <Row id="legend-grey-files" style="opacity: 0">
        <svg id="svg-legend">
            <g class="node" transform="translate(12.5,10)">
                <circle class="circle" r="7" style="fill: rgba(0,0,0,0.35);"></circle>
            </g>
        </svg>
        <div class="legend-label">&nbsp;- No-dup files</div>
    </Row>
</Overlay>
