import type { EChartsOption } from "echarts";

import type { ChartDatum, NetworkNode, VisualizationSpec } from "../types";

const networkColors: Record<NetworkNode["type"], string> = {
  drug: "#2563eb",
  sponsor: "#0891b2",
  condition: "#7c3aed",
  trial: "#ea580c",
  site: "#16a34a",
  country: "#475569",
};

function getField<T extends string | number>(datum: ChartDatum, field: string, fallback: T): T {
  const value = datum[field];
  return typeof value === typeof fallback ? (value as T) : fallback;
}

export function chartOption(visualization: VisualizationSpec): EChartsOption {
  if (visualization.type === "network_graph") {
    return {
      tooltip: {
        formatter: (params) => {
          if (Array.isArray(params)) {
            return "";
          }

          return String(params.name || params.value || "");
        },
      },
      legend: visualization.render_hints?.legend === false ? undefined : { top: 0 },
      series: [
        {
          type: "graph",
          name: visualization.render_hints?.series_name ?? "Network",
          layout: "force",
          roam: true,
          top: 36,
          draggable: true,
          force: { repulsion: 220, edgeLength: 120 },
          categories: Object.keys(networkColors).map((name) => ({ name })),
          label: { show: true, position: "right" },
          edgeLabel: { show: false },
          data: visualization.data.nodes.map((node) => ({
            id: node.id,
            name: node.label,
            category: node.type,
            value: node.value,
            symbolSize: Math.max(22, Math.min(54, (node.value ?? 6) * 2)),
            itemStyle: { color: networkColors[node.type] },
          })),
          links: visualization.data.edges.map((edge) => ({
            ...edge,
            lineStyle: { width: Math.max(1, Math.min(8, edge.weight / 3)) },
          })),
        },
      ],
    };
  }

  const xField = visualization.encoding.x;
  const yField = visualization.encoding.y;
  const hints = visualization.render_hints;

  if (visualization.type === "grouped_bar_chart") {
    const categoryField = hints?.category_field ?? xField;
    const groupField = hints?.group_field ?? visualization.encoding.group;
    const valueField = hints?.value_field ?? yField;
    const categories = Array.from(
      new Set(visualization.data.map((datum) => getField(datum, categoryField, ""))),
    );
    const groups = Array.from(
      new Set(visualization.data.map((datum) => getField(datum, groupField, ""))),
    );

    return {
      tooltip: { trigger: "axis" },
      legend: hints?.legend === false ? undefined : { top: 0 },
      grid: { top: 52, right: 24, bottom: 56, left: 64 },
      xAxis: { type: "category", name: hints?.x_axis_label, data: categories },
      yAxis: { type: "value", name: hints?.y_axis_label },
      series: groups.map((group) => ({
        type: "bar",
        name: group,
        data: categories.map((category) => {
          const match = visualization.data.find(
            (datum) =>
              getField(datum, categoryField, "") === category &&
              getField(datum, groupField, "") === group,
          );
          return match ? getField(match, valueField, 0) : 0;
        }),
      })),
    };
  }

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { top: 52, right: 24, bottom: 56, left: 64 },
    xAxis: {
      type: "category",
      name: hints?.x_axis_label,
      data: visualization.data.map((datum) => getField(datum, xField, "")),
    },
    yAxis: { type: "value", name: hints?.y_axis_label },
    series: [
      {
        type: visualization.type === "bar_chart" ? "bar" : "line",
        name: hints?.series_name ?? yField,
        smooth: visualization.type !== "bar_chart",
        data: visualization.data.map((datum) => getField(datum, yField, 0)),
        areaStyle: visualization.type === "time_series" ? {} : undefined,
      },
    ],
  };
}
