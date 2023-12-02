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

export type ReportData = {
    overlaps_report: OverlapsReport;
    file_to_string_mapping: FileToStringMapping;
};
