import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import type { VisualizationApiResponse, VisualizationRequest } from "../types";

export type ExampleSummary = {
  id: string;
  label: string;
  request: VisualizationRequest;
};

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const clinicalTrialsApi = createApi({
  reducerPath: "clinicalTrialsApi",
  baseQuery: fetchBaseQuery({ baseUrl: BASE_URL }),
  endpoints: (builder) => ({
    getExamples: builder.query<ExampleSummary[], void>({
      query: () => "/examples",
    }),
    postVisualization: builder.mutation<VisualizationApiResponse, VisualizationRequest>({
      query: (body) => ({
        url: "/visualizations",
        method: "POST",
        body,
      }),
    }),
  }),
});

export const { useGetExamplesQuery, usePostVisualizationMutation } = clinicalTrialsApi;
