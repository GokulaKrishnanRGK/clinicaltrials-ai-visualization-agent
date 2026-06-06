import type { EChartsOption } from "echarts";

import type { ChartDatum, ChartVisualizationSpec, NetworkNode, VisualizationSpec } from "../types";
import { COUNTRY_ALIASES } from "./worldMap";

const CHART_COLORS = ["#3b82f6", "#06b6d4", "#f59e0b", "#10b981", "#f43f5e", "#8b5cf6"];

const networkColors: Record<NetworkNode["type"], string> = {
  drug: "#3b82f6",
  sponsor: "#06b6d4",
  condition: "#8b5cf6",
  trial: "#f59e0b",
  site: "#10b981",
  country: "#f43f5e",
};

function cssVar(name: string, fallback: string): string {
  if (typeof document === "undefined") return fallback;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

function getField<T extends string | number>(datum: ChartDatum, field: string, fallback: T): T {
  const value = datum[field];
  return typeof value === typeof fallback ? (value as T) : fallback;
}

function xAxisLabel(itemCount: number) {
  const rotate = itemCount > 16 ? 55 : itemCount > 8 ? 38 : 0;
  const bottom = itemCount > 16 ? 105 : itemCount > 8 ? 85 : 56;
  const fontSize = itemCount > 20 ? 10 : 12;
  return { rotate, bottom, axisLabel: { interval: 0, rotate, fontSize } };
}

export function choroplethOption(visualization: ChartVisualizationSpec): EChartsOption {
  const xField = visualization.encoding.x;
  const yField = visualization.encoding.y;
  const hints = visualization.render_hints;

  const textColor = cssVar("--text-1", "#e2e8f0");
  const borderColor = cssVar("--border", "#2d3748");
  const areaColor = cssVar("--surface-2", "#1e2430");

  const data = visualization.data.map((datum) => {
    const raw = String(getField(datum, xField, ""));
    return { name: COUNTRY_ALIASES[raw] ?? raw, value: getField(datum, yField, 0) };
  });

  const maxVal = data.reduce((m, d) => Math.max(m, Number(d.value)), 1);

  return {
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        const p = params as { name: string; value?: number };
        return p.value != null
          ? `<strong>${p.name}</strong><br/>${hints?.y_axis_label ?? "Trials"}: ${p.value}`
          : p.name;
      },
    },
    visualMap: {
      min: 0,
      max: maxVal,
      left: 12,
      bottom: 12,
      orient: "vertical",
      text: ["High", "Low"],
      calculable: true,
      inRange: { color: ["#dbeafe", "#2563eb"] },
      textStyle: { color: textColor, fontSize: 11 },
    },
    series: [
      {
        type: "map",
        map: "world",
        roam: true,
        data,
        nameProperty: "name",
        itemStyle: { areaColor, borderColor, borderWidth: 0.5 },
        emphasis: {
          itemStyle: { areaColor: "#f59e0b" },
          label: { color: textColor, fontSize: 11 },
        },
        select: { disabled: true },
      },
    ],
  } as EChartsOption;
}

export function chartOption(visualization: VisualizationSpec): EChartsOption {
  if (visualization.type === "network_graph") {
    const labelColor = cssVar("--text-1", "#e2e8f0");
    const borderColor = cssVar("--surface", "#161b22");
    const edgeColor = cssVar("--border", "#2d3748");
    const legendTextColor = cssVar("--text-2", "#94a3b8");

    const labelStyle = {
      show: true,
      color: labelColor,
      textBorderColor: borderColor,
      textBorderWidth: 3,
      fontSize: 12,
      fontWeight: 500,
    } as const;

    return {
      tooltip: {
        formatter: (params) => {
          if (Array.isArray(params)) return "";
          if ((params as { dataType?: string }).dataType === "edge") {
            const d = params.data as { source: string; target: string; weight: number };
            return `${d.source} → ${d.target}<br/>weight: ${d.weight}`;
          }
          return `<strong>${params.name}</strong>${params.value ? `<br/>count: ${params.value}` : ""}`;
        },
      },
      legend:
        visualization.render_hints?.legend === false
          ? undefined
          : {
              orient: "vertical",
              right: 8,
              top: "middle",
              icon: "circle",
              itemWidth: 10,
              itemHeight: 10,
              textStyle: { color: legendTextColor, fontSize: 12 },
            },
      series: [
        {
          type: "graph",
          name: visualization.render_hints?.series_name ?? "Network",
          layout: "force",
          roam: true,
          draggable: true,
          force: {
            repulsion: 420,
            edgeLength: [120, 240],
            gravity: 0.06,
            friction: 0.65,
            layoutAnimation: true,
          },
          categories: Object.keys(networkColors).map((name) => ({ name })),
          label: { ...labelStyle, position: "right" },
          emphasis: {
            focus: "adjacency",
            label: { ...labelStyle, fontWeight: 700 },
          },
          edgeLabel: { show: false },
          lineStyle: { color: edgeColor, curveness: 0.2, opacity: 0.75 },
          data: visualization.data.nodes.map((node) => ({
            id: node.id,
            name: node.label,
            category: node.type,
            value: node.value,
            symbolSize: Math.max(26, Math.min(62, (node.value ?? 6) * 2.5)),
            itemStyle: { color: networkColors[node.type] },
            label: { ...labelStyle, position: "right" },
          })),
          links: visualization.data.edges.map((edge) => ({
            source: edge.source,
            target: edge.target,
            value: edge.weight,
            lineStyle: {
              width: Math.max(1, Math.min(6, edge.weight / 5)),
              color: edgeColor,
              curveness: 0.2,
              opacity: 0.75,
            },
          })),
        },
      ],
    };
  }

  const xField = visualization.encoding.x;
  const yField = visualization.encoding.y;
  const hints = visualization.render_hints;

  if (visualization.type === "scatter_chart") {
    return {
      color: CHART_COLORS,
      tooltip: {
        trigger: "item",
        formatter: (params) => {
          if (Array.isArray(params)) return "";
          const d = params.data as [number, number];
          return `${hints?.x_axis_label ?? xField}: ${d[0]}<br/>${hints?.y_axis_label ?? yField}: ${d[1]}`;
        },
      },
      grid: { top: 52, right: 24, bottom: 56, left: 64 },
      xAxis: { type: "value", name: hints?.x_axis_label, minInterval: 1 },
      yAxis: { type: "value", name: hints?.y_axis_label },
      series: [
        {
          type: "scatter",
          name: hints?.series_name ?? yField,
          symbolSize: 10,
          data: visualization.data.map((datum) => [
            getField(datum, xField, 0),
            getField(datum, yField, 0),
          ]),
        },
      ],
    };
  }

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
    const lbl = xAxisLabel(categories.length);

    return {
      color: CHART_COLORS,
      tooltip: { trigger: "axis" },
      legend: hints?.legend === false ? undefined : { top: 0 },
      grid: { top: 52, right: 24, bottom: lbl.bottom, left: 64 },
      xAxis: { type: "category", name: hints?.x_axis_label, data: categories, axisLabel: lbl.axisLabel },
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

  const lbl = xAxisLabel(visualization.data.length);

  return {
    color: CHART_COLORS,
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { top: 52, right: 24, bottom: lbl.bottom, left: 64 },
    xAxis: {
      type: "category",
      name: hints?.x_axis_label,
      data: visualization.data.map((datum) => {
        const v = datum[xField];
        return v !== null && v !== undefined && !Array.isArray(v) ? String(v) : "";
      }),
      axisLabel: lbl.axisLabel,
    },
    yAxis: { type: "value", name: hints?.y_axis_label },
    series: [
      {
        type: visualization.type === "bar_chart" || visualization.type === "histogram" ? "bar" : "line",
        name: hints?.series_name ?? yField,
        smooth: visualization.type !== "bar_chart",
        data: visualization.data.map((datum) => getField(datum, yField, 0)),
        areaStyle: visualization.type === "time_series" ? {} : undefined,
      },
    ],
  };
}
