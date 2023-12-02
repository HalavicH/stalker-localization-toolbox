type OverlapInfo = {
    total_id_cnt: number;
    match_count: number;
    overlapping_ids: string[];
};

type OverlapsReport = {
    [filePath: string]: {
        overlaps: {
            [overlapFilePath: string]: OverlapInfo;
        };
        total_id_cnt: number;
    };
};

type FileToStringMapping = {
    [filePath: string]: {
        [key: string]: number;
    };
};

export interface ReportData {
    overlaps_report: OverlapsReport;
    file_to_string_mapping: FileToStringMapping;
};

//
export interface Node {
    id: string;
    strings: string[];
    index: number;
    totalKeysCnt: number;
    hasDuplicates: boolean;
}

export interface Link {
    source: number;
    target: number;
    duplicateKeysCnt: number;
    duplicateKeys: string[];
    color: string;
}
