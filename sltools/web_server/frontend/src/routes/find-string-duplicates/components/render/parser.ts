import * as d3 from 'd3';
import type { ReportData } from '../../report';
import { hashCode } from '$lib/js/misc';

// Define TypeScript types for nodes and links
interface Node {
    id: string;
    strings: string[];
    index: number;
    totalKeysCnt: number;
    hasDuplicates: boolean;
}

interface Link {
    source: number;
    target: number;
    duplicateKeysCnt: number;
    duplicateKeys: string[];
    color: string;
}

export function extractData(report: ReportData, showAllFiles: boolean) {
    const { nodes, nodeMap } = createNodesArray(report, showAllFiles);
    const links: Link[] = [];

    for (const file in report.overlaps_report) {
        const sourceIndex = nodeMap[file];
        for (const overlapFile in report.overlaps_report[file].overlaps) {
            const targetIndex = nodeMap[overlapFile];
            const overlapInfo = report.overlaps_report[file].overlaps[overlapFile];
            const sortedOverlappingIds = overlapInfo.overlapping_ids.sort();
            const hash = Math.abs(hashCode(sortedOverlappingIds.join('')));
            links.push({
                source: sourceIndex,
                target: targetIndex,
                duplicateKeysCnt: overlapInfo.match_count,
                duplicateKeys: sortedOverlappingIds,
                color: d3.schemeCategory10[hash % 10],
            });
        }
    }

    return { nodes, links };
}

function createNodesArray(report: ReportData, showAllFiles: boolean) {
    const nodes: Node[] = [];
    const nodeMap: Record<string, number> = {};
    let index = 0;

    for (const file in report.file_to_string_mapping) {
        const hasDuplicates = !!report.overlaps_report[file];
        if (!showAllFiles && !hasDuplicates) {
            continue;
        }

        const strings = Object.keys(report.file_to_string_mapping[file]);
        nodes.push({
            id: file,
            strings: strings,
            index: index,
            totalKeysCnt: strings.length,
            hasDuplicates: hasDuplicates,
        });

        nodeMap[file] = index;
        index++;
    }

    return { nodes, nodeMap };
}
