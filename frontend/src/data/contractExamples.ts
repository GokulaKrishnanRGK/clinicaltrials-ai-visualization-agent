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
  filters: ResponseMetadata["filters"],
  records_retrieved: number,
  records_used: number,
): ResponseMetadata => ({
  source: "clinicaltrials.gov",
  filters,
  records_retrieved,
  records_used,
  generated_at: "2026-06-06T00:00:00Z",
});

export const examples: Example[] = [
  // ── Bar Charts ────────────────────────────────────────────────────────────
  {
    id: "bar",
    label: "Alzheimer's trials by country",
    category: "bar",
    chartType: "Bar Chart",
    toolCalls: 1,
    request: {
      query: "Which countries have the most recruiting Alzheimer's trials?",
      condition: "Alzheimer Disease",
      status: "recruiting",
      preferred_visualization: "bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_bar_001",
      visualization: {
        type: "bar_chart",
        title: "Recruiting Alzheimer's Trials by Country",
        description: "Top countries ranked by recruiting trial count.",
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
          { country: "United Kingdom", trial_count: 11, citations: [] },
          { country: "Japan", trial_count: 8, citations: [] },
          { country: "Germany", trial_count: 7, citations: [] },
          { country: "France", trial_count: 6, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Country",
          y_axis_label: "Trials",
          series_name: "Recruiting trials",
          sort: "desc",
        },
      },
      meta: baseMeta({ condition: "Alzheimer Disease", status: "RECRUITING" }, 85, 75),
      warnings: ["Country coverage excludes facilities without parsed locations."],
      assumptions: ["Countries were counted once per trial when multiple sites existed."],
    },
  },
  {
    id: "bar_status",
    label: "COVID-19 trials by status",
    category: "bar",
    chartType: "Bar Chart",
    toolCalls: 1,
    request: {
      query: "Show COVID-19 trials broken down by current status.",
      condition: "COVID-19",
      preferred_visualization: "bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_bar_002",
      visualization: {
        type: "bar_chart",
        title: "COVID-19 Trials by Study Status",
        description: "Distribution of registered COVID-19 trials across all status categories.",
        encoding: { x: "status", y: "trial_count" },
        data: [
          {
            status: "Completed",
            trial_count: 1842,
            citations: [
              citation(
                "NCT04280705",
                "protocolSection.statusModule.overallStatus",
                "COMPLETED",
                "Hydroxychloroquine in COVID-19",
              ),
            ],
          },
          {
            status: "Recruiting",
            trial_count: 631,
            citations: [
              citation(
                "NCT05848895",
                "protocolSection.statusModule.overallStatus",
                "RECRUITING",
                "Long COVID Rehabilitation Study",
              ),
            ],
          },
          { status: "Terminated", trial_count: 287, citations: [] },
          { status: "Active, not recruiting", trial_count: 209, citations: [] },
          { status: "Not yet recruiting", trial_count: 154, citations: [] },
          { status: "Withdrawn", trial_count: 98, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Status",
          y_axis_label: "Trials",
          series_name: "Trial count",
          sort: "desc",
        },
      },
      meta: baseMeta({ condition: "COVID-19" }, 3221, 3221),
      warnings: [],
      assumptions: ["Status labels are normalized from overallStatus field values."],
    },
  },
  {
    id: "bar_sponsors",
    label: "Top oncology sponsors",
    category: "bar",
    chartType: "Bar Chart",
    toolCalls: 1,
    request: {
      query: "Which sponsors have the most active recruiting oncology trials?",
      condition: "Neoplasms",
      status: "recruiting",
      preferred_visualization: "bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_bar_003",
      visualization: {
        type: "bar_chart",
        title: "Top Sponsors by Recruiting Oncology Trials",
        description: "Industry and institutional sponsors ranked by active trial count.",
        encoding: { x: "sponsor", y: "trial_count" },
        data: [
          {
            sponsor: "Pfizer",
            trial_count: 84,
            citations: [
              citation(
                "NCT05422170",
                "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
                "Pfizer",
                "Palbociclib in Solid Tumors",
              ),
            ],
          },
          {
            sponsor: "Roche",
            trial_count: 76,
            citations: [
              citation(
                "NCT04909931",
                "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
                "Hoffmann-La Roche",
                "Atezolizumab Combination Study",
              ),
            ],
          },
          { sponsor: "AstraZeneca", trial_count: 71, citations: [] },
          { sponsor: "Merck", trial_count: 68, citations: [] },
          { sponsor: "Novartis", trial_count: 62, citations: [] },
          { sponsor: "Bristol-Myers Squibb", trial_count: 54, citations: [] },
          { sponsor: "AbbVie", trial_count: 48, citations: [] },
          { sponsor: "Eli Lilly", trial_count: 44, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Sponsor",
          y_axis_label: "Trials",
          series_name: "Active trials",
          sort: "desc",
        },
      },
      meta: baseMeta({ condition: "Neoplasms", status: "RECRUITING" }, 1842, 511),
      warnings: ["Sponsor names are taken from leadSponsor.name and may have minor variations."],
      assumptions: ["Only lead sponsors are counted; collaborating organizations are excluded."],
    },
  },

  // ── Comparison (Grouped Bar) ───────────────────────────────────────────────
  {
    id: "grouped",
    label: "Oncology phase × sponsor class",
    category: "comparison",
    chartType: "Grouped Bar",
    toolCalls: 1,
    request: {
      query: "Compare Phase 2 and Phase 3 oncology trials by sponsor class.",
      condition: "Neoplasms",
      start_year: 2021,
      end_year: 2025,
      preferred_visualization: "grouped_bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_grouped_001",
      visualization: {
        type: "grouped_bar_chart",
        title: "Oncology Trials by Phase and Sponsor Class",
        description: "Trial counts split by phase and sponsor class (2021–2025).",
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
                "KRAS G12C Inhibitor Study",
              ),
            ],
          },
          {
            phase: "PHASE2",
            sponsor_class: "NIH",
            trial_count: 16,
            citations: [],
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
                "Lung Cancer Survival Study",
              ),
            ],
          },
          { phase: "PHASE3", sponsor_class: "NIH", trial_count: 9, citations: [] },
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
      meta: baseMeta({ condition: "Neoplasms", start_year: 2021, end_year: 2025 }, 142, 127),
      warnings: [],
      assumptions: ["Trials with multiple phases were counted under their most specific phase."],
    },
  },
  {
    id: "grouped_hf",
    label: "Heart failure phase × sponsor",
    category: "comparison",
    chartType: "Grouped Bar",
    toolCalls: 1,
    request: {
      query: "Compare heart failure trial phases between industry and academic sponsors.",
      condition: "Heart Failure",
      preferred_visualization: "grouped_bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_grouped_002",
      visualization: {
        type: "grouped_bar_chart",
        title: "Heart Failure Trials by Phase and Sponsor Class",
        description: "Phase distribution comparing industry versus academic/other sponsors.",
        encoding: { x: "phase", y: "trial_count", group: "sponsor_class" },
        data: [
          {
            phase: "PHASE1",
            sponsor_class: "INDUSTRY",
            trial_count: 12,
            citations: [
              citation(
                "NCT04981678",
                "protocolSection.designModule.phases",
                "PHASE1",
                "Novel HFrEF Dose Escalation Study",
              ),
            ],
          },
          { phase: "PHASE1", sponsor_class: "OTHER", trial_count: 8, citations: [] },
          {
            phase: "PHASE2",
            sponsor_class: "INDUSTRY",
            trial_count: 36,
            citations: [
              citation(
                "NCT05322122",
                "protocolSection.designModule.phases",
                "PHASE2",
                "Empagliflozin in HFpEF",
              ),
            ],
          },
          { phase: "PHASE2", sponsor_class: "OTHER", trial_count: 22, citations: [] },
          {
            phase: "PHASE3",
            sponsor_class: "INDUSTRY",
            trial_count: 28,
            citations: [
              citation(
                "NCT03057977",
                "protocolSection.designModule.phases",
                "PHASE3",
                "EMPEROR-Preserved Trial",
              ),
            ],
          },
          { phase: "PHASE3", sponsor_class: "OTHER", trial_count: 11, citations: [] },
          { phase: "PHASE4", sponsor_class: "INDUSTRY", trial_count: 18, citations: [] },
          { phase: "PHASE4", sponsor_class: "OTHER", trial_count: 5, citations: [] },
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
      meta: baseMeta({ condition: "Heart Failure" }, 188, 140),
      warnings: [],
      assumptions: ["Academic, hospital, and government sponsors are grouped under OTHER."],
    },
  },
  {
    id: "compare_drugs",
    label: "Pembrolizumab vs Nivolumab",
    category: "comparison",
    chartType: "Grouped Bar",
    toolCalls: 2,
    request: {
      query: "Compare Pembrolizumab vs Nivolumab phase distribution.",
      preferred_visualization: "grouped_bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_cmp_drugs_001",
      visualization: {
        type: "grouped_bar_chart",
        title: "Pembrolizumab vs Nivolumab — Trial Phase Distribution",
        description: "Phase distribution for each drug fetched from separate ClinicalTrials.gov queries.",
        encoding: { x: "phase", y: "trial_count", group: "label" },
        data: [
          {
            phase: "PHASE1",
            label: "Pembrolizumab",
            trial_count: 21,
            citations: [
              citation(
                "NCT02129660",
                "protocolSection.designModule.phases",
                "PHASE1",
                "Pembrolizumab Dose-Escalation Study",
              ),
            ],
          },
          { phase: "PHASE1", label: "Nivolumab", trial_count: 17, citations: [] },
          {
            phase: "PHASE2",
            label: "Pembrolizumab",
            trial_count: 134,
            citations: [
              citation(
                "NCT02564263",
                "protocolSection.designModule.phases",
                "PHASE2",
                "Pembrolizumab in Advanced Melanoma",
              ),
            ],
          },
          {
            phase: "PHASE2",
            label: "Nivolumab",
            trial_count: 109,
            citations: [
              citation(
                "NCT01721746",
                "protocolSection.designModule.phases",
                "PHASE2",
                "Nivolumab in Solid Tumors",
              ),
            ],
          },
          { phase: "PHASE3", label: "Pembrolizumab", trial_count: 92, citations: [] },
          { phase: "PHASE3", label: "Nivolumab", trial_count: 78, citations: [] },
          { phase: "PHASE4", label: "Pembrolizumab", trial_count: 14, citations: [] },
          { phase: "PHASE4", label: "Nivolumab", trial_count: 9, citations: [] },
          { phase: "NA", label: "Pembrolizumab", trial_count: 63, citations: [] },
          { phase: "NA", label: "Nivolumab", trial_count: 34, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Phase",
          y_axis_label: "Trials",
          group_field: "label",
          category_field: "phase",
          value_field: "trial_count",
          legend: true,
        },
      },
      meta: baseMeta({}, 573, 431),
      warnings: [],
      assumptions: [
        "Each drug was fetched independently; totals reflect separate API queries.",
        "Phase NA includes trials with no phase information recorded.",
      ],
    },
  },
  {
    id: "compare_countries",
    label: "US vs Germany — oncology",
    category: "comparison",
    chartType: "Grouped Bar",
    toolCalls: 2,
    request: {
      query: "Compare oncology trials in the United States vs Germany by phase.",
      condition: "Neoplasms",
      preferred_visualization: "grouped_bar_chart",
      max_records: 400,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_cmp_geo_001",
      visualization: {
        type: "grouped_bar_chart",
        title: "US vs Germany — Oncology Trial Phase Distribution",
        description: "Trial counts by phase for each country fetched from separate queries.",
        encoding: { x: "phase", y: "trial_count", group: "label" },
        data: [
          {
            phase: "PHASE1",
            label: "United States",
            trial_count: 58,
            citations: [
              citation(
                "NCT04898634",
                "protocolSection.contactsLocationsModule.locations",
                "United States",
                "Dose Escalation Study — NSCLC",
              ),
            ],
          },
          {
            phase: "PHASE1",
            label: "Germany",
            trial_count: 22,
            citations: [
              citation(
                "NCT05312723",
                "protocolSection.contactsLocationsModule.locations",
                "Germany",
                "Early-Phase Solid Tumor Trial",
              ),
            ],
          },
          { phase: "PHASE2", label: "United States", trial_count: 112, citations: [] },
          { phase: "PHASE2", label: "Germany", trial_count: 41, citations: [] },
          { phase: "PHASE3", label: "United States", trial_count: 76, citations: [] },
          { phase: "PHASE3", label: "Germany", trial_count: 38, citations: [] },
          { phase: "PHASE4", label: "United States", trial_count: 19, citations: [] },
          { phase: "PHASE4", label: "Germany", trial_count: 11, citations: [] },
          { phase: "NA", label: "United States", trial_count: 31, citations: [] },
          { phase: "NA", label: "Germany", trial_count: 14, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Phase",
          y_axis_label: "Trials",
          group_field: "label",
          category_field: "phase",
          value_field: "trial_count",
          legend: true,
        },
      },
      meta: baseMeta({ condition: "Neoplasms" }, 422, 422),
      warnings: [],
      assumptions: [
        "Trials without a country listed in their locations module are excluded.",
        "A trial may appear in both countries if it has sites in each.",
      ],
    },
  },
  {
    id: "compare_status",
    label: "Recruiting vs completed — Alzheimer's",
    category: "comparison",
    chartType: "Grouped Bar",
    toolCalls: 2,
    request: {
      query: "Compare recruiting vs completed Alzheimer's trials by phase.",
      condition: "Alzheimer Disease",
      preferred_visualization: "grouped_bar_chart",
      max_records: 400,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_cmp_status_001",
      visualization: {
        type: "grouped_bar_chart",
        title: "Alzheimer's Trials — Recruiting vs Completed by Phase",
        description: "Phase breakdown for actively recruiting versus completed Alzheimer's trials.",
        encoding: { x: "phase", y: "trial_count", group: "label" },
        data: [
          {
            phase: "PHASE1",
            label: "Recruiting",
            trial_count: 9,
            citations: [
              citation(
                "NCT05476926",
                "protocolSection.statusModule.overallStatus",
                "RECRUITING",
                "Anti-Tau Antibody Phase 1 Study",
              ),
            ],
          },
          {
            phase: "PHASE1",
            label: "Completed",
            trial_count: 31,
            citations: [
              citation(
                "NCT01262183",
                "protocolSection.statusModule.overallStatus",
                "COMPLETED",
                "Aducanumab Phase 1b Safety Study",
              ),
            ],
          },
          { phase: "PHASE2", label: "Recruiting", trial_count: 24, citations: [] },
          { phase: "PHASE2", label: "Completed", trial_count: 68, citations: [] },
          { phase: "PHASE3", label: "Recruiting", trial_count: 18, citations: [] },
          { phase: "PHASE3", label: "Completed", trial_count: 42, citations: [] },
          { phase: "PHASE4", label: "Recruiting", trial_count: 6, citations: [] },
          { phase: "PHASE4", label: "Completed", trial_count: 14, citations: [] },
          { phase: "NA", label: "Recruiting", trial_count: 12, citations: [] },
          { phase: "NA", label: "Completed", trial_count: 27, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Phase",
          y_axis_label: "Trials",
          group_field: "label",
          category_field: "phase",
          value_field: "trial_count",
          legend: true,
        },
      },
      meta: baseMeta({ condition: "Alzheimer Disease" }, 251, 251),
      warnings: [],
      assumptions: [
        "Each status was fetched independently from ClinicalTrials.gov.",
        "Phase NA includes trials with no phase designation.",
      ],
    },
  },

  // ── Time Series ───────────────────────────────────────────────────────────
  {
    id: "line",
    label: "Diabetes enrollment trend",
    category: "time",
    chartType: "Line Chart",
    toolCalls: 1,
    request: {
      query: "Show median enrollment for completed diabetes trials by year.",
      condition: "Diabetes Mellitus",
      status: "completed",
      preferred_visualization: "line_chart",
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
      meta: baseMeta({ condition: "Diabetes Mellitus", status: "COMPLETED" }, 96, 83),
      warnings: ["Enrollment is planned or actual depending on the source record field."],
      assumptions: [],
    },
  },
  {
    id: "time",
    label: "Pembrolizumab trial starts",
    category: "time",
    chartType: "Time Series",
    toolCalls: 1,
    request: {
      query: "How many Pembrolizumab trials started each year since 2015?",
      drug_name: "Pembrolizumab",
      start_year: 2015,
      preferred_visualization: "time_series",
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
      meta: baseMeta({ drug_name: "Pembrolizumab", start_year: 2015 }, 126, 114),
      warnings: [],
      assumptions: ["Start year was derived from startDateStruct.date when available."],
    },
  },
  {
    id: "time_covid",
    label: "COVID registrations 2020–2024",
    category: "time",
    chartType: "Time Series",
    toolCalls: 1,
    request: {
      query: "How did new COVID-19 trial registrations change between 2020 and 2024?",
      condition: "COVID-19",
      start_year: 2020,
      end_year: 2024,
      preferred_visualization: "time_series",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_time_002",
      visualization: {
        type: "time_series",
        title: "New COVID-19 Trial Registrations by Year",
        description: "Annual volume of new COVID-19 trial registrations on ClinicalTrials.gov.",
        encoding: { x: "year", y: "new_trials" },
        data: [
          {
            year: 2020,
            new_trials: 1724,
            citations: [
              citation(
                "NCT04280705",
                "protocolSection.statusModule.startDateStruct.date",
                "2020-03-09",
                "Hydroxychloroquine in COVID-19",
              ),
            ],
          },
          { year: 2021, new_trials: 892, citations: [] },
          { year: 2022, new_trials: 541, citations: [] },
          {
            year: 2023,
            new_trials: 318,
            citations: [
              citation(
                "NCT05848895",
                "protocolSection.statusModule.startDateStruct.date",
                "2023-06-12",
                "Long COVID Rehabilitation Study",
              ),
            ],
          },
          { year: 2024, new_trials: 204, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Year",
          y_axis_label: "New registrations",
          series_name: "New registrations",
          sort: "chronological",
        },
      },
      meta: baseMeta({ condition: "COVID-19", start_year: 2020, end_year: 2024 }, 3679, 3679),
      warnings: [],
      assumptions: [
        "Year is derived from the first-submitted date, not the trial's actual start date.",
      ],
    },
  },

  // ── Networks ──────────────────────────────────────────────────────────────
  {
    id: "network",
    label: "Immunotherapy sponsor network",
    category: "network",
    chartType: "Network",
    toolCalls: 1,
    request: {
      query: "Map sponsors connected to immunotherapy conditions.",
      condition: "Immunotherapy",
      preferred_visualization: "network_graph",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_network_001",
      visualization: {
        type: "network_graph",
        title: "Immunotherapy Sponsor and Condition Network",
        description: "Sponsor, condition, and drug nodes connected by study relationships.",
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
            { id: "pembro", label: "Pembrolizumab", type: "drug", value: 31, citations: [] },
            { id: "melanoma", label: "Melanoma", type: "condition", value: 12, citations: [] },
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
            { source: "merck", target: "pembro", weight: 24, relation: "sponsors", citations: [] },
            { source: "pembro", target: "melanoma", weight: 12, relation: "studies", citations: [] },
            { source: "pembro", target: "lung", weight: 18, relation: "studies", citations: [] },
            { source: "bristol", target: "melanoma", weight: 9, relation: "studies", citations: [] },
          ],
        },
        render_hints: { series_name: "Study relationships", legend: true },
      },
      meta: baseMeta({ condition: "Immunotherapy" }, 62, 48),
      warnings: ["Edges aggregate matching trial relationships and are not causal links."],
      assumptions: [],
    },
  },
  {
    id: "network_glp1",
    label: "GLP-1 drug co-occurrence network",
    category: "network",
    chartType: "Network",
    toolCalls: 1,
    request: {
      query: "Show how GLP-1 drugs like semaglutide and tirzepatide connect to conditions.",
      condition: "Obesity",
      preferred_visualization: "network_graph",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_network_002",
      visualization: {
        type: "network_graph",
        title: "GLP-1 Drug and Condition Co-occurrence Network",
        description:
          "Drugs, conditions, and lead sponsors connected by co-occurrence in registered trials.",
        encoding: { node: "label", link: "relation", weight: "weight" },
        data: {
          nodes: [
            {
              id: "sema",
              label: "Semaglutide",
              type: "drug",
              value: 38,
              citations: [
                citation(
                  "NCT03548935",
                  "protocolSection.armsInterventionsModule.interventions.name",
                  "Semaglutide",
                  "SUSTAIN-6 Cardiovascular Outcomes",
                ),
              ],
            },
            {
              id: "tirze",
              label: "Tirzepatide",
              type: "drug",
              value: 22,
              citations: [
                citation(
                  "NCT04496102",
                  "protocolSection.armsInterventionsModule.interventions.name",
                  "Tirzepatide",
                  "SURMOUNT-1 Obesity Study",
                ),
              ],
            },
            { id: "liraglu", label: "Liraglutide", type: "drug", value: 14, citations: [] },
            { id: "obesity", label: "Obesity", type: "condition", value: 44, citations: [] },
            {
              id: "t2dm",
              label: "Type 2 Diabetes",
              type: "condition",
              value: 31,
              citations: [
                citation(
                  "NCT03457259",
                  "protocolSection.conditionsModule.conditions",
                  "Type 2 Diabetes Mellitus",
                  "PIONEER Oral Semaglutide Trial",
                ),
              ],
            },
            { id: "nash", label: "MASH / NAFLD", type: "condition", value: 12, citations: [] },
            {
              id: "novo",
              label: "Novo Nordisk",
              type: "sponsor",
              value: 52,
              citations: [
                citation(
                  "NCT03457259",
                  "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
                  "Novo Nordisk A/S",
                  "PIONEER Oral Semaglutide Trial",
                ),
              ],
            },
            { id: "lilly", label: "Eli Lilly", type: "sponsor", value: 22, citations: [] },
          ],
          edges: [
            { source: "novo", target: "sema", weight: 38, relation: "sponsors", citations: [] },
            { source: "lilly", target: "tirze", weight: 22, relation: "sponsors", citations: [] },
            { source: "novo", target: "liraglu", weight: 14, relation: "sponsors", citations: [] },
            { source: "sema", target: "obesity", weight: 28, relation: "studies", citations: [] },
            { source: "sema", target: "t2dm", weight: 22, relation: "studies", citations: [] },
            { source: "tirze", target: "t2dm", weight: 18, relation: "studies", citations: [] },
            { source: "tirze", target: "obesity", weight: 14, relation: "studies", citations: [] },
            { source: "sema", target: "nash", weight: 8, relation: "studies", citations: [] },
            { source: "liraglu", target: "t2dm", weight: 14, relation: "studies", citations: [] },
          ],
        },
        render_hints: { series_name: "Co-occurrence", legend: true },
      },
      meta: baseMeta({ condition: "Obesity" }, 142, 116),
      warnings: [],
      assumptions: [
        "Co-occurrence edges count shared trials, not direct pharmacological interactions.",
      ],
    },
  },

  // ── Advanced ──────────────────────────────────────────────────────────────
  {
    id: "scatter",
    label: "Oncology trial complexity by year",
    category: "advanced",
    chartType: "Scatter",
    toolCalls: 1,
    request: {
      query: "Show how oncology trial intervention counts changed by start year.",
      condition: "Neoplasms",
      start_year: 2018,
      end_year: 2024,
      preferred_visualization: "scatter_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_scatter_001",
      visualization: {
        type: "scatter_chart",
        title: "Avg Interventions per Oncology Trial by Start Year",
        description:
          "Average number of study arms/interventions per trial, plotted by start year as a proxy for trial complexity.",
        encoding: { x: "start_year", y: "avg_interventions" },
        data: [
          { start_year: 2018, avg_interventions: 2.1, trial_count: 84, citations: [] },
          {
            start_year: 2019,
            avg_interventions: 2.4,
            trial_count: 97,
            citations: [
              citation(
                "NCT03892525",
                "protocolSection.armsInterventionsModule.interventions.name",
                "Pembrolizumab",
                "Pembrolizumab + Chemo Combo Study",
              ),
            ],
          },
          { start_year: 2020, avg_interventions: 2.2, trial_count: 91, citations: [] },
          {
            start_year: 2021,
            avg_interventions: 2.6,
            trial_count: 112,
            citations: [
              citation(
                "NCT04895618",
                "protocolSection.armsInterventionsModule.interventions.name",
                "Nivolumab",
                "Nivolumab + Ipilimumab NSCLC Study",
              ),
            ],
          },
          { start_year: 2022, avg_interventions: 2.8, trial_count: 118, citations: [] },
          { start_year: 2023, avg_interventions: 3.0, trial_count: 104, citations: [] },
          { start_year: 2024, avg_interventions: 2.9, trial_count: 78, citations: [] },
        ],
        render_hints: {
          x_axis_label: "Start year",
          y_axis_label: "Avg interventions per trial",
          series_name: "Avg interventions",
        },
      },
      meta: baseMeta({ condition: "Neoplasms", start_year: 2018, end_year: 2024 }, 684, 684),
      warnings: ["Intervention count counts named arms; placebo arms are included."],
      assumptions: ["Years with fewer than 5 trials are excluded from this sample."],
    },
  },
  {
    id: "histogram",
    label: "COVID-19 trial year distribution",
    category: "advanced",
    chartType: "Histogram",
    toolCalls: 1,
    request: {
      query: "Show the distribution of COVID-19 trial registrations across year ranges.",
      condition: "COVID-19",
      preferred_visualization: "histogram",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "visualization",
      request_id: "req_hist_001",
      visualization: {
        type: "histogram",
        title: "COVID-19 Trial Registrations — Year Distribution",
        description:
          "Frequency histogram of COVID-19 trial start years, showing the surge and decline in registrations.",
        encoding: { x: "range_label", y: "trial_count" },
        data: [
          {
            range_label: "2019–2020",
            min_year: 2019,
            max_year: 2020,
            trial_count: 1748,
            citations: [
              citation(
                "NCT04280705",
                "protocolSection.statusModule.startDateStruct.date",
                "2020-03-09",
                "Hydroxychloroquine in COVID-19",
              ),
            ],
          },
          {
            range_label: "2021–2022",
            min_year: 2021,
            max_year: 2022,
            trial_count: 1433,
            citations: [],
          },
          {
            range_label: "2023–2024",
            min_year: 2023,
            max_year: 2024,
            trial_count: 522,
            citations: [],
          },
        ],
        render_hints: {
          x_axis_label: "Year range",
          y_axis_label: "Trials registered",
          series_name: "Trials registered",
        },
      },
      meta: baseMeta({ condition: "COVID-19" }, 3703, 3703),
      warnings: [],
      assumptions: [
        "Start year is derived from startDateStruct.date; trials with no date are excluded.",
        "Bins span two calendar years to reduce bin count for readability.",
      ],
    },
  },

  // ── System ────────────────────────────────────────────────────────────────
  {
    id: "message",
    label: "Out-of-scope query",
    category: "system",
    chartType: "Message",
    toolCalls: 0,
    request: {
      query: "What is the best recipe for chocolate chip cookies?",
      preferred_visualization: "bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "message",
      request_id: "req_msg_001",
      message:
        "This application only answers questions about clinical trials — drugs, conditions, trial phases, sponsors, enrollment, and related topics. Please rephrase your question around clinical trial data.",
      reason: "unsupported_query",
      suggested_queries: [
        "Show trials for semaglutide by phase",
        "How many Alzheimer's trials are active in the US?",
        "Top sponsors for oncology trials",
      ],
      meta: null,
    },
  },
  {
    id: "insufficient",
    label: "Insufficient data response",
    category: "system",
    chartType: "Message",
    toolCalls: 1,
    request: {
      query: "Find active trials for a brand-new experimental intervention with no registered studies.",
      preferred_visualization: "bar_chart",
      max_records: 500,
      citation_limit: 10,
    },
    response: {
      status: "message",
      request_id: "req_msg_002",
      message:
        "Not enough trial data was found to generate a meaningful visualization. The query returned fewer than 3 usable records after filtering. Try broadening your search — remove specific status or phase filters, or use a wider date range.",
      reason: "insufficient_data",
      suggested_queries: [
        "Show all oncology trials by phase",
        "Alzheimer's trials recruiting in the US",
        "COVID-19 trial registrations by year",
      ],
      meta: null,
    },
  },
];
