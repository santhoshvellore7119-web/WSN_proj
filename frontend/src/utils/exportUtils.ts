import { SimulationResults } from '../types';

/**
 * Exports simulation round-by-round time series and summary metrics to a standard CSV file.
 */
export function exportSimulationCSV(results: SimulationResults, customFilename?: string): void {
  if (!results) return;

  const summary = results.summary;
  const ts = results.time_series;
  const cfg = results.configuration;

  const lines: string[] = [];

  // Header metadata comments
  lines.push(`# WSN Energy-Harvesting Simulation Report`);
  lines.push(`# Algorithm: ${cfg.routing_algorithm.toUpperCase()} | Profile: ${cfg.harvesting_profile.toUpperCase()} | Nodes: ${cfg.nodes} | Rounds: ${cfg.rounds}`);
  lines.push(`# FND Round: ${summary.first_node_death_round ?? 'N/A'} | Final Alive Nodes: ${summary.final_alive_nodes}/${summary.total_nodes} | Final Total Energy: ${summary.final_total_energy.toFixed(4)} J`);
  lines.push(`# Total Harvested: ${summary.total_harvested_energy.toFixed(4)} J | Total Consumed: ${summary.total_consumed_energy.toFixed(4)} J | Total Reroutes: ${summary.total_reroutes}`);
  lines.push(``);

  // CSV Column headers
  lines.push(`round,alive_nodes,total_energy_joules,harvested_energy_joules,consumed_energy_joules,reroute_events,jains_fairness_index,packet_delivery_ratio`);

  // Data rows
  const numRows = ts.rounds.length;
  for (let i = 0; i < numRows; i++) {
    const r = ts.rounds[i];
    const alive = ts.alive_nodes[i] ?? 0;
    const energy = (ts.total_energy[i] ?? 0).toFixed(6);
    const harv = (ts.harvested_energy[i] ?? 0).toFixed(6);
    const cons = (ts.consumed_energy[i] ?? 0).toFixed(6);
    const reroutes = ts.reroute_events[i] ?? 0;
    const fairness = (ts.fairness_index[i] ?? 1.0).toFixed(4);
    const pdr = (ts.pdr_history[i] ?? 1.0).toFixed(4);

    lines.push(`${r},${alive},${energy},${harv},${cons},${reroutes},${fairness},${pdr}`);
  }

  const csvContent = lines.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const filename = customFilename || `wsn_sim_${cfg.routing_algorithm}_${cfg.harvesting_profile}_${timestamp}.csv`;

  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Exports an SVG element as a standalone, downloadable .svg file.
 */
export function exportSvgElement(svgElement: SVGSVGElement | null, filename: string = 'network_topology.svg'): void {
  if (!svgElement) return;

  const serializer = new XMLSerializer();
  let source = serializer.serializeToString(svgElement);

  // Add standard SVG namespace attributes if not present
  if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  if (!source.match(/^<svg[^>]+xmlns\:xlink="http\:\/\/www\.w3\.org\/1999\/xlink"/)) {
    source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
  }

  // XML declaration prefix
  source = '<?xml version="1.0" standalone="no"?>\r\n' + source;

  const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
