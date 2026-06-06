import * as echarts from "echarts";

const WORLD_JSON_URL = "https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/world.json";

let _registered = false;
let _pending: Promise<boolean> | null = null;

export function isWorldMapRegistered(): boolean {
  return _registered;
}

export async function ensureWorldMap(): Promise<boolean> {
  if (_registered) return true;
  if (!_pending) {
    _pending = fetch(WORLD_JSON_URL)
      .then((r) => r.json())
      .then((json) => {
        echarts.registerMap("world", json);
        _registered = true;
        return true;
      })
      .catch(() => {
        _pending = null;
        return false;
      });
  }
  return _pending;
}

/**
 * Maps CT.gov country names (ISO/UN formal names) to Natural Earth names
 * used by the echarts v4 world map GeoJSON.
 */
export const COUNTRY_ALIASES: Record<string, string> = {
  "Korea, Republic of": "South Korea",
  "Korea, Democratic People's Republic of": "North Korea",
  "Russian Federation": "Russia",
  "Iran, Islamic Republic of": "Iran",
  "Syrian Arab Republic": "Syria",
  "Viet Nam": "Vietnam",
  "Czech Republic": "Czech Rep.",
  "Czechia": "Czech Rep.",
  "Bolivia, Plurinational State of": "Bolivia",
  "Venezuela, Bolivarian Republic of": "Venezuela",
  "Tanzania, United Republic of": "Tanzania",
  "Taiwan, Province of China": "Taiwan",
  "Moldova, Republic of": "Moldova",
  "Lao People's Democratic Republic": "Laos",
  "Congo, Democratic Republic of the": "Dem. Rep. Congo",
  "Congo, Republic of the": "Republic of Congo",
  "Côte d'Ivoire": "Ivory Coast",
  "Macedonia, the Former Yugoslav Republic of": "Macedonia",
  "Palestine, State of": "Palestine",
  "Libya": "Libya",
  "Myanmar": "Myanmar",
  "United Kingdom": "United Kingdom",
  "United States": "United States",
};
