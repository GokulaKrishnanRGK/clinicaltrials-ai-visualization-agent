import type { Example, ResponseMetadata, SourceCitation } from "../types";

const citation = (
  nct_id: string,
  field: string,
  value: string | number,
  brief_title: string,
): SourceCitation => ({
  nct_id,
  field,
  value,
  brief_title,
});

const baseMeta = (
  data_mode: "cache" | "live",
  filters: ResponseMetadata["filters"],
  records_retrieved: number,
  records_used: number,
): ResponseMetadata => ({
  source: "clinicaltrials.gov",
  data_mode,
  filters,
  records_retrieved,
  records_used,
  generated_at: "2026-06-06T00:00:00Z",
});

export const examples: Example[] = [
  {
    id: "bar",
    label: "Recruiting trials by country",
    request: {
      query: "Which countries have the most recruiting Alzheimer's trials?",
      condition: "Alzheimer Disease",
      status: "recruiting",
      preferred_visualization: "bar_chart",
      data_mode: "cache",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_bar_001",
      visualization: {
        type: "bar_chart",
        title: "Recruiting Alzheimer's Trials by Country",
        description: "Top cached countries ranked by recruiting trial count.",
        encoding: { x: "country", y: "trial_count" },
        data: [
          {
            country: "United States",
            trial_count: 42,
            citations: [
              citation(
                "NCT04108943",
                "protocolSection.contactsLocationsModule.locations",
                "United States",
                "Aducanumab in Early Alzheimer's Disease",
              ),
            ],
          },
          {
            country: "Canada",
            trial_count: 14,
            citations: [
              citation(
                "NCT04777396",
                "protocolSection.contactsLocationsModule.locations",
                "Canada",
                "Tau PET Imaging in Dementia",
              ),
            ],
          },
          {
            country: "United Kingdom",
            trial_count: 11,
            citations: [
              citation(
                "NCT04468659",
                "protocolSection.contactsLocationsModule.locations",
                "United Kingdom",
                "Memory Clinic Recruitment Study",
              ),
            ],
          },
          {
            country: "Japan",
            trial_count: 8,
            citations: [
              citation(
                "NCT05269394",
                "protocolSection.statusModule.overallStatus",
                "RECRUITING",
                "Amyloid Reduction Follow-up",
              ),
            ],
          },
        ],
        render_hints: {
          x_axis_label: "Country",
          y_axis_label: "Trials",
          series_name: "Recruiting trials",
          sort: "desc",
        },
      },
      meta: baseMeta("cache", { condition: "Alzheimer Disease", status: "RECRUITING" }, 85, 75),
      warnings: ["Cached country coverage excludes facilities without parsed locations."],
      assumptions: ["Countries were counted once per trial when multiple sites existed."],
    },
  },
  {
    id: "grouped",
    label: "Phase by sponsor class",
    request: {
      query: "Compare Phase 2 and Phase 3 oncology trials by sponsor class.",
      condition: "Neoplasms",
      start_year: 2021,
      end_year: 2025,
      preferred_visualization: "grouped_bar_chart",
      data_mode: "cache",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_grouped_001",
      visualization: {
        type: "grouped_bar_chart",
        title: "Oncology Trials by Phase and Sponsor Class",
        description: "Cached oncology trial counts split by phase and sponsor class.",
        encoding: { x: "phase", y: "trial_count", group: "sponsor_class" },
        data: [
          {
            phase: "PHASE2",
            sponsor_class: "INDUSTRY",
            trial_count: 58,
            citations: [
              citation(
                "NCT05065078",
                "protocolSection.designModule.phases",
                "PHASE2",
                "KRAS Study",
              ),
            ],
          },
          {
            phase: "PHASE2",
            sponsor_class: "NIH",
            trial_count: 16,
            citations: [
              citation(
                "NCT04448217",
                "protocolSection.sponsorCollaboratorsModule.leadSponsor.class",
                "NIH",
                "Immunotherapy Combination Study",
              ),
            ],
          },
          {
            phase: "PHASE3",
            sponsor_class: "INDUSTRY",
            trial_count: 44,
            citations: [
              citation(
                "NCT04586270",
                "protocolSection.designModule.phases",
                "PHASE3",
                "Lung Cancer Trial",
              ),
            ],
          },
          {
            phase: "PHASE3",
            sponsor_class: "NIH",
            trial_count: 9,
            citations: [
              citation(
                "NCT03964571",
                "protocolSection.sponsorCollaboratorsModule.leadSponsor.class",
                "NIH",
                "NCI-Sponsored Therapy Trial",
              ),
            ],
          },
        ],
        render_hints: {
          x_axis_label: "Trial phase",
          y_axis_label: "Trials",
          group_field: "sponsor_class",
          category_field: "phase",
          value_field: "trial_count",
          legend: true,
        },
      },
      meta: baseMeta(
        "cache",
        { condition: "Neoplasms", start_year: 2021, end_year: 2025 },
        142,
        127,
      ),
      warnings: [],
      assumptions: ["Trials with multiple phases were counted under their most specific phase."],
    },
  },
  {
    id: "line",
    label: "Enrollment trend",
    request: {
      query: "Show median enrollment for completed diabetes trials by year.",
      condition: "Diabetes Mellitus",
      status: "completed",
      preferred_visualization: "line_chart",
      data_mode: "cache",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_line_001",
      visualization: {
        type: "line_chart",
        title: "Median Enrollment in Completed Diabetes Trials",
        encoding: { x: "year", y: "median_enrollment" },
        data: [
          { year: 2020, median_enrollment: 72, citations: [] },
          {
            year: 2021,
            median_enrollment: 86,
            citations: [
              citation(
                "NCT04635984",
                "protocolSection.designModule.enrollmentInfo.count",
                86,
                "Glucose Monitoring Outcomes",
              ),
            ],
          },
          { year: 2022, median_enrollment: 92, citations: [] },
          { year: 2023, median_enrollment: 88, citations: [] },
          {
            year: 2024,
            median_enrollment: 104,
            citations: [
              citation(
                "NCT05980104",
                "protocolSection.designModule.enrollmentInfo.count",
                104,
                "Metabolic Outcomes Study",
              ),
            ],
          },
        ],
        render_hints: {
          x_axis_label: "Completion year",
          y_axis_label: "Median enrollment",
          series_name: "Median enrollment",
          sort: "chronological",
        },
      },
      meta: baseMeta("cache", { condition: "Diabetes Mellitus", status: "COMPLETED" }, 96, 83),
      warnings: ["Enrollment is planned or actual depending on the source record field."],
      assumptions: [],
    },
  },
  {
    id: "time",
    label: "Pembrolizumab starts",
    request: {
      query: "How many Pembrolizumab trials started each year since 2015?",
      drug_name: "Pembrolizumab",
      start_year: 2015,
      preferred_visualization: "time_series",
      data_mode: "cache",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_time_001",
      visualization: {
        type: "time_series",
        title: "Pembrolizumab Trial Starts by Year",
        encoding: { x: "year", y: "trial_count" },
        data: [
          { year: 2019, trial_count: 18, citations: [] },
          {
            year: 2020,
            trial_count: 21,
            citations: [
              citation(
                "NCT04380636",
                "protocolSection.statusModule.startDateStruct.date",
                "2020-05-06",
                "Pembrolizumab With Chemotherapy",
              ),
            ],
          },
          { year: 2021, trial_count: 25, citations: [] },
          { year: 2022, trial_count: 20, citations: [] },
          {
            year: 2023,
            trial_count: 17,
            citations: [
              citation(
                "NCT05705573",
                "protocolSection.armsInterventionsModule.interventions.name",
                "Pembrolizumab",
                "Adjuvant Pembrolizumab Study",
              ),
            ],
          },
          { year: 2024, trial_count: 13, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Start year",
          y_axis_label: "Trials",
          series_name: "Trial starts",
          sort: "chronological",
        },
      },
      meta: baseMeta("cache", { drug_name: "Pembrolizumab", start_year: 2015 }, 126, 114),
      warnings: [],
      assumptions: ["Start year was derived from startDateStruct.date when available."],
    },
  },
  {
    id: "network",
    label: "Sponsor-condition network",
    request: {
      query: "Map sponsors connected to immunotherapy conditions.",
      condition: "Immunotherapy",
      preferred_visualization: "network_graph",
      data_mode: "cache",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_network_001",
      visualization: {
        type: "network_graph",
        title: "Immunotherapy Sponsor and Condition Network",
        description: "Sponsor, condition, and drug nodes connected by cached study relationships.",
        encoding: { node: "label", link: "relation", weight: "weight" },
        data: {
          nodes: [
            {
              id: "merck",
              label: "Merck Sharp & Dohme",
              type: "sponsor",
              value: 24,
              citations: [
                citation(
                  "NCT04380636",
                  "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
                  "Merck Sharp & Dohme LLC",
                  "Pembrolizumab With Chemotherapy",
                ),
              ],
            },
            {
              id: "pembro",
              label: "Pembrolizumab",
              type: "drug",
              value: 31,
              citations: [],
            },
            {
              id: "melanoma",
              label: "Melanoma",
              type: "condition",
              value: 12,
              citations: [],
            },
            {
              id: "lung",
              label: "Non-Small Cell Lung Cancer",
              type: "condition",
              value: 18,
              citations: [],
            },
            {
              id: "bristol",
              label: "Bristol-Myers Squibb",
              type: "sponsor",
              value: 17,
              citations: [],
            },
          ],
          edges: [
            {
              source: "merck",
              target: "pembro",
              weight: 24,
              relation: "sponsors",
              citations: [],
            },
            {
              source: "pembro",
              target: "melanoma",
              weight: 12,
              relation: "studies",
              citations: [],
            },
            {
              source: "pembro",
              target: "lung",
              weight: 18,
              relation: "studies",
              citations: [],
            },
            {
              source: "bristol",
              target: "melanoma",
              weight: 9,
              relation: "studies",
              citations: [],
            },
          ],
        },
        render_hints: {
          series_name: "Study relationships",
          legend: true,
        },
      },
      meta: baseMeta("cache", { condition: "Immunotherapy" }, 62, 48),
      warnings: ["Edges aggregate matching trial relationships and are not causal links."],
      assumptions: [],
    },
  },
  {
    id: "message",
    label: "Cache miss message",
    request: {
      query: "Find brand-new live trial updates for a rare intervention.",
      preferred_visualization: "bar_chart",
      data_mode: "cache",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "message",
      request_id: "req_msg_001",
      message:
        "This query is not available in cache mode. Switch to live mode or choose a canned example.",
      reason: "cache_miss",
      suggested_queries: [
        "How many Pembrolizumab trials started each year since 2015?",
        "Which countries have the most recruiting Alzheimer's trials?",
      ],
      meta: null,
    },
  },
];
