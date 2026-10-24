import React, { useState, useRef } from 'react';
import { NodePosition, SimulationConfig, SimulationResults } from '../types';
import { exportSvgElement, exportSimulationCSV } from '../utils/exportUtils';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Eye,
  Zap,
  Radio,
  Share2,
  Info,
  Flame,
  Download,
  FileSpreadsheet,
  Percent,
  Sun,
  Cloud,
  Pin,
  X,
  ShieldCheck,
  ShieldAlert
} from 'lucide-react';

interface NetworkTopologyViewProps {
  results: SimulationResults | null;
  config: SimulationConfig;
  currentRound?: number;
}

// Computes a high-contrast, continuous color and status metadata from battery ratio
export function getNodeEnergyVisual(ratio: number, isAlive: boolean) {
  if (!isAlive || ratio <= 0.0005) {
    return {
      fill: '#13161f',
      stroke: '#475569',
      ringColor: '#334155',
      textColor: '#94a3b8',
      badgeBg: 'rgba(30, 41, 59, 0.85)',
      label: 'Depleted',
      glow: 'transparent'
    };
  }
  if (ratio >= 0.85) {
    return {
      fill: '#064e3b',
      stroke: '#10b981',
      ringColor: '#34d399',
      textColor: '#6ee7b7',
      badgeBg: 'rgba(6, 78, 59, 0.75)',
      label: 'Full (85-100%)',
      glow: 'rgba(16, 185, 129, 0.45)'
    };
  }
  if (ratio >= 0.70) {
    return {
      fill: '#0f766e',
      stroke: '#14b8a6',
      ringColor: '#2dd4bf',
      textColor: '#5eead4',
      badgeBg: 'rgba(15, 118, 110, 0.75)',
      label: 'High (70-85%)',
      glow: 'rgba(20, 184, 166, 0.4)'
    };
  }
  if (ratio >= 0.50) {
    return {
      fill: '#0e7490',
      stroke: '#06b6d4',
      ringColor: '#38bdf8',
      textColor: '#7dd3fc',
      badgeBg: 'rgba(14, 116, 144, 0.75)',
      label: 'Good (50-70%)',
      glow: 'rgba(6, 182, 212, 0.35)'
    };
  }
  if (ratio >= 0.35) {
    return {
      fill: '#4d7c0f',
      stroke: '#84cc16',
      ringColor: '#a3e635',
      textColor: '#bef264',
      badgeBg: 'rgba(77, 124, 15, 0.75)',
      label: 'Moderate (35-50%)',
      glow: 'rgba(132, 204, 22, 0.35)'
    };
  }
  if (ratio >= 0.20) {
    return {
      fill: '#b45309',
      stroke: '#f59e0b',
      ringColor: '#fbbf24',
      textColor: '#fde047',
      badgeBg: 'rgba(180, 83, 9, 0.75)',
      label: 'Low (20-35%)',
      glow: 'rgba(245, 158, 11, 0.4)'
    };
  }
  if (ratio >= 0.08) {
    return {
      fill: '#c2410c',
      stroke: '#f97316',
      ringColor: '#fb923c',
      textColor: '#fdba74',
      badgeBg: 'rgba(194, 65, 12, 0.75)',
      label: 'Depleting (8-20%)',
      glow: 'rgba(249, 115, 22, 0.4)'
    };
  }
  return {
    fill: '#991b1b',
    stroke: '#ef4444',
    ringColor: '#f87171',
    textColor: '#fca5a5',
    badgeBg: 'rgba(153, 27, 27, 0.75)',
    label: 'Critical (<8%)',
    glow: 'rgba(239, 68, 68, 0.5)'
  };
}

export const NetworkTopologyView: React.FC<NetworkTopologyViewProps> = ({
  results,
  config,
  currentRound = 0
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredNodeId, setHoveredNodeId] = useState<number | null>(null);
  const [pinnedNodeId, setPinnedNodeId] = useState<number | null>(null);

  // Layer Toggles
  const [showClusters, setShowClusters] = useState<boolean>(true);
  const [showRoutes, setShowRoutes] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [showPercentages, setShowPercentages] = useState<boolean>(true);
  const [showHeatmap, setShowHeatmap] = useState<boolean>(false);
  const [displayMode, setDisplayMode] = useState<'truth' | 'belief' | 'error'>('truth');

  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const areaSize = config.area || 100;
  const numNodes = config.nodes || 50;

  // Extract current round state
  const roundIdx = results
    ? Math.min(currentRound, (results.detailed_data.energy_matrix.length || 1) - 1)
    : 0;

  const nodePositions: Record<string, NodePosition> = results?.detailed_data.node_positions || {};
  const energyMatrix = results?.detailed_data.energy_matrix;
  const chHistory = results?.detailed_data.cluster_heads_history;
  const routesHistory = results?.detailed_data.routes_history;
  const clusterAssignments = results?.detailed_data.cluster_assignments_history;
  const shadowMultipliers = results?.detailed_data.node_shadow_multipliers || {};
  const beliefMatrix = results?.detailed_data.belief_matrix;
  const varianceMatrix = results?.detailed_data.variance_matrix;
  const initialEnergies = results?.detailed_data.node_initial_energies || {};

  const currentCHs = chHistory && chHistory[roundIdx] ? chHistory[roundIdx] : [];
  const currentRoutes = routesHistory && routesHistory[roundIdx] ? routesHistory[roundIdx] : {};
  const currentAssignments = clusterAssignments && clusterAssignments[roundIdx] ? clusterAssignments[roundIdx] : {};

  // Base station coordinates
  const bsX = config.bs_x !== undefined ? config.bs_x : areaSize / 2;
  const bsY = config.bs_y !== undefined ? config.bs_y : areaSize / 2;

  // Identify active relay nodes in the current multi-hop routes
  const activeRelayNodeIds = new Set<number>();
  Object.values(currentRoutes).forEach(([path]) => {
    if (path && path.length > 2) {
      for (let i = 1; i < path.length - 1; i++) {
        if (path[i] !== -1) activeRelayNodeIds.add(path[i]);
      }
    }
  });

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom(prev => Math.min(Math.max(prev * zoomFactor, 0.5), 4));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  const resetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleExportSvg = () => {
    if (svgRef.current) {
      exportSvgElement(svgRef.current, `wsn_topology_r${roundIdx}.svg`);
    }
  };

  const handleExportCsv = () => {
    if (results) {
      exportSimulationCSV(results);
    }
  };

  // Build node data with physical truth vs belief state & exact percentage
  const nodes = [];
  let fullCount = 0;
  let goodCount = 0;
  let modCount = 0;
  let lowCount = 0;
  let deadCount = 0;
  let shadedCount = 0;
  let sunlitCount = 0;

  for (let i = 0; i < numNodes; i++) {
    const pos = nodePositions[i] || {
      x: (i * 19.3 + 13) % areaSize,
      y: (i * 27.7 + 17) % areaSize
    };

    // Staggered initial heterogeneity fallback if not yet simulated
    const defaultInit = config.initial_energy_distribution === 'staggered'
      ? Math.max(0.02, config.init_energy * (0.4 + (i * 1.3) % 1.2))
      : config.init_energy;

    const initEnergy = initialEnergies[i] !== undefined ? initialEnergies[i] : defaultInit;
    const residual = energyMatrix && energyMatrix[roundIdx] ? energyMatrix[roundIdx][i] : initEnergy;
    const believedEnergy = beliefMatrix && beliefMatrix[roundIdx] ? beliefMatrix[roundIdx][i] : initEnergy;
    const beliefVar = varianceMatrix && varianceMatrix[roundIdx] ? varianceMatrix[roundIdx][i] : 0.0;
    const beliefStd = Math.sqrt(Math.max(0, beliefVar));
    const estimationError = Math.abs(residual - believedEnergy);

    const isAlive = residual > 1e-6;
    const isCH = currentCHs.includes(i);
    const isRelay = activeRelayNodeIds.has(i);
    const clusterId = currentAssignments[i] !== undefined ? currentAssignments[i] : (isCH ? i : null);
    const shadowMul = shadowMultipliers[i] !== undefined ? shadowMultipliers[i] : 1.0;
    const isShaded = shadowMul < 0.6;
    const maxEnergy = config.max_capacity || 0.50;
    
    const trueRatio = Math.max(0, Math.min(1, residual / maxEnergy));
    const beliefRatio = Math.max(0, Math.min(1, believedEnergy / maxEnergy));
    
    // Choose active ratio based on user-selected Display Mode
    let activeRatio = trueRatio;
    if (displayMode === 'belief') {
      activeRatio = beliefRatio;
    } else if (displayMode === 'error') {
      activeRatio = Math.max(0, Math.min(1, (estimationError * 6.0) / maxEnergy));
    }

    if (!isAlive) deadCount++;
    else if (trueRatio >= 0.70) fullCount++;
    else if (trueRatio >= 0.40) goodCount++;
    else if (trueRatio >= 0.20) modCount++;
    else lowCount++;

    if (isShaded) shadedCount++;
    else sunlitCount++;

    const visual = getNodeEnergyVisual(activeRatio, isAlive);

    nodes.push({
      id: i,
      x: pos.x,
      y: pos.y,
      initEnergy,
      residual,
      believedEnergy,
      beliefStd,
      estimationError,
      energyRatio: activeRatio,
      trueEnergyRatio: trueRatio,
      beliefEnergyRatio: beliefRatio,
      percentage: Math.round(activeRatio * 100),
      truePercentage: Math.round(trueRatio * 100),
      beliefPercentage: Math.round(beliefRatio * 100),
      isAlive,
      isCH,
      isRelay,
      clusterId,
      shadowMul,
      isShaded,
      visual
    });
  }

  const activeInspectId = pinnedNodeId !== null ? pinnedNodeId : hoveredNodeId;
  const activeInspectNode = activeInspectId !== null ? nodes.find(n => n.id === activeInspectId) : null;

  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden relative">
      {/* Top Toolbar */}
      <div className="p-2.5 bg-[#050608] border-b border-[#1b1d26] flex flex-wrap items-center justify-between gap-2 z-10">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5">
            <Radio className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold tracking-wide text-slate-100">
              Topology ({areaSize}m × {areaSize}m)
            </span>
          </div>
          {results && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#10131d] text-emerald-300 border border-[#1e2a3a]">
              Round {roundIdx} / {config.rounds}
            </span>
          )}
          {config.initial_energy_distribution && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#131722] text-amber-300 border border-[#2d281a] hidden sm:inline-block">
              {config.initial_energy_distribution.toUpperCase()} INIT
            </span>
          )}
        </div>

        {/* View toggles & Controls */}
        <div className="flex items-center gap-1.5 text-xs flex-wrap">
          {/* Display Mode: Truth vs Router Belief vs Telemetry Error */}
          <div className="flex items-center bg-[#07080c] p-0.5 rounded border border-[#1c1e28]">
            <button
              onClick={() => setDisplayMode('truth')}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1.5 transition-colors ${
                displayMode === 'truth' ? 'bg-[#064e3b] text-emerald-300 font-bold border border-[#10b981]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Physical Truth: True Continuous Electrochemical Charge"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Truth</span>
            </button>
            <button
              onClick={() => setDisplayMode('belief')}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1.5 transition-colors ${
                displayMode === 'belief' ? 'bg-[#0e7490] text-cyan-200 font-bold border border-[#06b6d4]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Digital Twin Belief: Router Believed Distribution"
            >
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>Belief (±σ)</span>
            </button>
            <button
              onClick={() => setDisplayMode('error')}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1.5 transition-colors ${
                displayMode === 'error' ? 'bg-[#7c2d12] text-amber-200 font-bold border border-[#ea580c]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Estimation Error: |Physical Truth - Digital Twin Belief|"
            >
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <span>Error</span>
            </button>
          </div>

          {/* Visibility Toggles */}
          <div className="flex items-center bg-[#07080c] p-0.5 rounded border border-[#1c1e28]">
            <button
              onClick={() => setShowPercentages(!showPercentages)}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 transition-colors ${
                showPercentages ? 'bg-[#1e293b] text-emerald-300 font-bold border border-[#38bdf8]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle Live Battery Percentage on Nodes"
            >
              <Percent className="w-3 h-3 text-emerald-400" />
              <span>Charge %</span>
            </button>
            <button
              onClick={() => setShowLabels(!showLabels)}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 transition-colors ${
                showLabels ? 'bg-[#181a24] text-slate-100 font-medium border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle Node IDs"
            >
              <Eye className="w-3 h-3" />
              <span>IDs</span>
            </button>
            <button
              onClick={() => setShowRoutes(!showRoutes)}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 transition-colors ${
                showRoutes ? 'bg-[#181a24] text-slate-100 font-medium border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle Multi-Hop Routing Paths"
            >
              <Zap className="w-3 h-3 text-amber-400" />
              <span>Routes</span>
            </button>
            <button
              onClick={() => setShowClusters(!showClusters)}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 transition-colors ${
                showClusters ? 'bg-[#181a24] text-slate-100 font-medium border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle Cluster Associations"
            >
              <Share2 className="w-3 h-3" />
              <span>Clusters</span>
            </button>
            <button
              onClick={() => setShowHeatmap(!showHeatmap)}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 transition-colors ${
                showHeatmap ? 'bg-[#1e1a12] text-amber-300 font-medium border border-[#3e341a]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle Heatmap"
            >
              <Flame className="w-3 h-3 text-orange-400" />
              <span>Heatmap</span>
            </button>
          </div>

          {/* Export & Zoom */}
          <div className="flex items-center bg-[#07080c] p-0.5 rounded border border-[#1c1e28]">
            <button
              onClick={handleExportSvg}
              className="px-2 py-1 text-slate-300 hover:text-slate-100 rounded text-[11px] flex items-center gap-1 hover:bg-[#14161f]"
              title="Export SVG Graphic"
            >
              <Download className="w-3 h-3" />
              <span>SVG</span>
            </button>
            {results && (
              <button
                onClick={handleExportCsv}
                className="px-2 py-1 text-slate-300 hover:text-slate-100 rounded text-[11px] flex items-center gap-1 hover:bg-[#14161f]"
                title="Export CSV"
              >
                <FileSpreadsheet className="w-3 h-3 text-emerald-400" />
                <span>CSV</span>
              </button>
            )}
            <button
              onClick={() => setZoom(prev => Math.min(prev * 1.2, 4))}
              className="p-1 text-slate-400 hover:text-slate-200 rounded"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoom(prev => Math.max(prev * 0.8, 0.5))}
              className="p-1 text-slate-400 hover:text-slate-200 rounded"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={resetZoom}
              className="p-1 text-slate-400 hover:text-slate-200 rounded"
              title="Reset View"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Interactive Canvas Area */}
      <div
        ref={containerRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="flex-1 w-full h-[530px] bg-black relative overflow-hidden cursor-grab active:cursor-grabbing select-none"
      >
        <svg
          ref={svgRef}
          className="w-full h-full"
          viewBox={`0 0 600 600`}
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Grid Pattern */}
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#121520" strokeWidth="0.75" />
            </pattern>
            {/* Shadow Zone Hatch Pattern */}
            <pattern id="shadowHatch" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2="10" stroke="#1f2538" strokeWidth="2.5" opacity="0.65" />
            </pattern>
            {/* Radial Glow Filters */}
            <radialGradient id="emeraldGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.45" />
              <stop offset="60%" stopColor="#059669" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#047857" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="amberGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.4" />
              <stop offset="60%" stopColor="#d97706" stopOpacity="0.12" />
              <stop offset="100%" stopColor="#b45309" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="redGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.45" />
              <stop offset="60%" stopColor="#b91c1c" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#7f1d1d" stopOpacity="0" />
            </radialGradient>
          </defs>

          <g transform={`translate(${pan.x + 300}, ${pan.y + 300}) scale(${zoom}) translate(-300, -300)`}>
            {/* Background Grid */}
            <rect x="0" y="0" width="600" height="600" fill="url(#grid)" />
            <rect x="0" y="0" width="600" height="600" fill="none" stroke="#22283a" strokeWidth="1.2" />

            {/* Heatmap Overlay Field */}
            {showHeatmap && nodes.map((node) => {
              if (!node.isAlive) return null;
              const cx = (node.x / areaSize) * 600;
              const cy = (node.y / areaSize) * 600;
              const glowRadius = Math.max(16, node.energyRatio * 65);
              const gradId = node.energyRatio > 0.5 ? 'emeraldGlow' : node.energyRatio > 0.2 ? 'amberGlow' : 'redGlow';
              return (
                <circle
                  key={`heat-${node.id}`}
                  cx={cx}
                  cy={cy}
                  r={glowRadius}
                  fill={`url(#${gradId})`}
                  style={{ mixBlendMode: 'screen' }}
                />
              );
            })}

            {/* Shadow Zone Boundary */}
            {(config.harvesting_profile === 'shadowed_solar' || shadedCount > 0) && (
              <g>
                <rect
                  x="0"
                  y="0"
                  width="600"
                  height={600 * (config.shadow_fraction || 0.35)}
                  fill="url(#shadowHatch)"
                />
                <line
                  x1="0"
                  y1={600 * (config.shadow_fraction || 0.35)}
                  x2="600"
                  y2={600 * (config.shadow_fraction || 0.35)}
                  stroke="#38435d"
                  strokeWidth="1.2"
                  strokeDasharray="4 4"
                />
                <text
                  x="12"
                  y="22"
                  fill="#94a3b8"
                  fontSize="11"
                  fontWeight="bold"
                  fontFamily="monospace"
                  letterSpacing="0.05em"
                >
                  ☁ SHADED CANOPY ZONE (~30% SOLAR IRRADIANCE)
                </text>
              </g>
            )}

            {/* Cluster Member Association Links */}
            {showClusters && nodes.map((node) => {
              if (!node.isAlive || node.isCH || node.clusterId === null) return null;
              const chNode = nodes.find(n => n.id === node.clusterId && n.isAlive);
              if (!chNode) return null;

              const x1 = (node.x / areaSize) * 600;
              const y1 = (node.y / areaSize) * 600;
              const x2 = (chNode.x / areaSize) * 600;
              const y2 = (chNode.y / areaSize) * 600;

              return (
                <line
                  key={`cluster-${node.id}-${chNode.id}`}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="#334155"
                  strokeWidth="0.8"
                  strokeDasharray="2 3"
                  opacity="0.45"
                />
              );
            })}

            {/* Multi-Hop Routing Paths to Base Station */}
            {showRoutes && Object.entries(currentRoutes).map(([chIdStr, routeData]) => {
              const chId = parseInt(chIdStr);
              const path = routeData[0];
              if (!path || path.length === 0) return null;

              const pathSegments = [];
              for (let idx = 0; idx < path.length - 1; idx++) {
                const u = path[idx];
                const v = path[idx + 1];

                const uNode = nodes.find(n => n.id === u);
                const uX = uNode ? (uNode.x / areaSize) * 600 : (bsX / areaSize) * 600;
                const uY = uNode ? (uNode.y / areaSize) * 600 : (bsY / areaSize) * 600;

                let vX, vY;
                if (v === -1) {
                  vX = (bsX / areaSize) * 600;
                  vY = (bsY / areaSize) * 600;
                } else {
                  const vNode = nodes.find(n => n.id === v);
                  vX = vNode ? (vNode.x / areaSize) * 600 : (bsX / areaSize) * 600;
                  vY = vNode ? (vNode.y / areaSize) * 600 : (bsY / areaSize) * 600;
                }

                const uEnergyRatio = uNode ? uNode.energyRatio : 1.0;
                let linkColor = '#10b981';
                if (uEnergyRatio < 0.20) linkColor = '#ef4444';
                else if (uEnergyRatio < 0.50) linkColor = '#f59e0b';
                else if (uEnergyRatio < 0.75) linkColor = '#06b6d4';

                pathSegments.push(
                  <g key={`route-${chId}-${u}-${v}-${idx}`}>
                    <line
                      x1={uX}
                      y1={uY}
                      x2={vX}
                      y2={vY}
                      stroke={linkColor}
                      strokeWidth="2.2"
                      strokeLinecap="round"
                    />
                    <circle
                      cx={(uX + vX) / 2}
                      cy={(uY + vY) / 2}
                      r="2.5"
                      fill={linkColor}
                    />
                  </g>
                );
              }
              return pathSegments;
            })}

            {/* Base Station Node */}
            {(() => {
              const bsCanvasX = (bsX / areaSize) * 600;
              const bsCanvasY = (bsY / areaSize) * 600;
              return (
                <g transform={`translate(${bsCanvasX}, ${bsCanvasY})`}>
                  <circle r="18" fill="none" stroke="#ef4444" strokeWidth="1" strokeDasharray="3 3" opacity="0.7" />
                  <rect
                    x="-10"
                    y="-10"
                    width="20"
                    height="20"
                    rx="3"
                    fill="#991b1b"
                    stroke="#f87171"
                    strokeWidth="1.5"
                  />
                  <polygon points="0,-6 -6,4 6,4" fill="#ffffff" />
                  <text
                    y="22"
                    textAnchor="middle"
                    fill="#f1f5f9"
                    fontSize="11"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    BS SINK ({bsX.toFixed(0)},{bsY.toFixed(0)})
                  </text>
                </g>
              );
            })()}

            {/* Individual Sensor Nodes (Differentiated Rendering) */}
            {nodes.map((node) => {
              const cx = (node.x / areaSize) * 600;
              const cy = (node.y / areaSize) * 600;
              const isHovered = hoveredNodeId === node.id;
              const isPinned = pinnedNodeId === node.id;
              const isSelected = isHovered || isPinned;

              const coreRadius = node.isCH ? 8.5 : 7.0;
              const gaugeRadius = node.isCH ? 12.0 : 10.0;
              const circumference = 2 * Math.PI * gaugeRadius;
              const strokeOffset = circumference * (1 - node.energyRatio);

              return (
                <g
                  key={`node-${node.id}`}
                  transform={`translate(${cx}, ${cy})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setPinnedNodeId(prev => prev === node.id ? null : node.id);
                  }}
                  onMouseEnter={() => setHoveredNodeId(node.id)}
                  onMouseLeave={() => setHoveredNodeId(null)}
                  className="cursor-pointer"
                >
                  {/* Selected / Hover Ring */}
                  {isSelected && (
                    <circle
                      r={gaugeRadius + 5}
                      fill="none"
                      stroke={isPinned ? '#38bdf8' : '#e2e8f0'}
                      strokeWidth="1.8"
                      strokeDasharray="3 3"
                    />
                  )}

                  {/* Active Relay Traffic Pulse */}
                  {node.isRelay && node.isAlive && (
                    <circle
                      r={gaugeRadius + 4}
                      fill="none"
                      stroke="#06b6d4"
                      strokeWidth="1.5"
                      strokeDasharray="4 2"
                      opacity="0.85"
                    />
                  )}

                  {/* Uncertainty Halo (Belief Mode) */}
                  {displayMode === 'belief' && node.isAlive && node.beliefStd > 0.0005 && (
                    <circle
                      r={gaugeRadius + Math.min(16, 4 + node.beliefStd * 260)}
                      fill="none"
                      stroke="#38bdf8"
                      strokeWidth="1.2"
                      strokeDasharray="2 3"
                      opacity="0.7"
                    />
                  )}

                  {/* Estimation Error Divergence Aura (Error Mode) */}
                  {displayMode === 'error' && node.isAlive && node.estimationError > 0.001 && (
                    <circle
                      r={gaugeRadius + Math.min(16, 4 + (node.estimationError * 200))}
                      fill="none"
                      stroke="#f59e0b"
                      strokeWidth="1.2"
                      strokeDasharray="2 2"
                      opacity="0.8"
                    />
                  )}

                  {/* Outer Circular Energy Gauge Track */}
                  <circle
                    r={gaugeRadius}
                    fill="none"
                    stroke="#171b26"
                    strokeWidth="2.5"
                  />

                  {/* Outer Circular Energy Gauge Fill */}
                  {node.isAlive && (
                    <circle
                      r={gaugeRadius}
                      fill="none"
                      stroke={node.visual.stroke}
                      strokeWidth="2.5"
                      strokeDasharray={`${circumference} ${circumference}`}
                      strokeDashoffset={strokeOffset}
                      strokeLinecap="round"
                      transform="rotate(-90)"
                    />
                  )}

                  {/* Central Node Core */}
                  <circle
                    r={coreRadius}
                    fill={node.visual.fill}
                    stroke={node.isCH ? '#fbbf24' : '#000000'}
                    strokeWidth={node.isCH ? 1.8 : 1.0}
                  />

                  {/* Dead Node Icon */}
                  {!node.isAlive && (
                    <g stroke="#f87171" strokeWidth="1.5">
                      <line x1="-3.5" y1="-3.5" x2="3.5" y2="3.5" />
                      <line x1="3.5" y1="-3.5" x2="-3.5" y2="3.5" />
                    </g>
                  )}

                  {/* Sun / Shade Indicator Dot */}
                  {node.isAlive && (
                    <circle
                      cx={coreRadius - 1}
                      cy={-coreRadius + 1}
                      r="2.2"
                      fill={node.isShaded ? '#64748b' : '#fbbf24'}
                      stroke="#050608"
                      strokeWidth="0.5"
                    />
                  )}

                  {/* Node ID Label */}
                  {showLabels && (
                    <g transform={`translate(0, ${node.isCH ? -15 : -13})`}>
                      <rect
                        x="-14"
                        y="-8"
                        width="28"
                        height="10"
                        rx="2"
                        fill="rgba(5, 6, 8, 0.85)"
                        stroke="#1f2433"
                        strokeWidth="0.5"
                      />
                      <text
                        y="-1"
                        textAnchor="middle"
                        fill={node.isCH ? '#fbbf24' : '#e2e8f0'}
                        fontSize="8.5"
                        fontWeight={node.isCH ? 'bold' : '600'}
                        fontFamily="monospace"
                      >
                        {node.isCH ? `CH${node.id}` : `N${node.id}`}
                      </text>
                    </g>
                  )}

                  {/* Exact Energy Percentage Badge */}
                  {showPercentages && (
                    <g transform={`translate(0, ${gaugeRadius + 9})`}>
                      <rect
                        x="-13"
                        y="-7"
                        width="26"
                        height="10"
                        rx="2"
                        fill={node.visual.badgeBg}
                        stroke={node.visual.stroke}
                        strokeWidth="0.5"
                      />
                      <text
                        y="0.5"
                        textAnchor="middle"
                        fill={node.visual.textColor}
                        fontSize="8"
                        fontWeight="bold"
                        fontFamily="monospace"
                      >
                        {node.percentage}%
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Live Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-[#06070af0] p-2.5 rounded border border-[#1e2333] text-[10px] space-y-1.5 pointer-events-none z-10 shadow-2xl backdrop-blur-sm">
          <div className="font-bold text-slate-200 flex items-center justify-between pb-1 border-b border-[#1b1f2e]">
            <div className="flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-emerald-400" />
              <span>Node States & Energy Scale</span>
            </div>
            <span className="text-[9px] text-slate-400 font-mono">({nodes.length} Motes)</span>
          </div>

          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] inline-block"></span>
              <span className="text-slate-200">85-100% (Full)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#06b6d4] inline-block"></span>
              <span className="text-slate-200">50-85% (Good)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b] inline-block"></span>
              <span className="text-slate-200">20-50% (Moderate)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444] inline-block"></span>
              <span className="text-slate-200">&lt;20% (Critical)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#fbbf24] border border-amber-300 inline-block"></span>
              <span className="text-amber-300 font-semibold">Cluster Head</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#334155] border border-slate-500 inline-block"></span>
              <span className="text-slate-400">Depleted (0%)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#fbbf24]"></span>
              <span className="text-slate-300">☀ Sunlit Mote</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#64748b]"></span>
              <span className="text-slate-300">☁ Shaded Mote</span>
            </div>
          </div>
        </div>

        {/* Detailed Node Inspector Card (Hover or Pinned) */}
        {activeInspectNode && (
          <div className="absolute top-3 right-3 bg-[#06070be8] p-3 rounded-lg border border-[#23293d] text-xs w-72 z-20 space-y-2 shadow-2xl backdrop-blur-md">
            <div className="flex items-center justify-between pb-1.5 border-b border-[#1c2234]">
              <div className="flex items-center gap-1.5">
                {pinnedNodeId === activeInspectNode.id && (
                  <Pin className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" />
                )}
                <span className="font-bold font-mono text-slate-100 text-sm">
                  Node #{activeInspectNode.id}
                </span>
                {activeInspectNode.isCH && (
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-[#fbbf24]/20 text-[#fbbf24] border border-[#fbbf24]/40">
                    CH
                  </span>
                )}
                {activeInspectNode.isRelay && (
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-[#06b6d4]/20 text-[#38bdf8] border border-[#06b6d4]/40">
                    RELAY
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                  activeInspectNode.isAlive ? 'bg-[#064e3b] text-emerald-300 border border-[#10b981]' : 'bg-[#7f1d1d] text-rose-300 border border-[#ef4444]'
                }`}>
                  {activeInspectNode.isAlive ? `${activeInspectNode.percentage}%` : 'DEAD'}
                </span>
                {pinnedNodeId === activeInspectNode.id && (
                  <button
                    onClick={() => setPinnedNodeId(null)}
                    className="p-0.5 text-slate-400 hover:text-slate-100 rounded"
                    title="Unpin Card"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-1.5 text-[11px] text-slate-200">
              <div className="flex justify-between items-center bg-[#0d111a] px-2 py-1 rounded">
                <span className="text-slate-400">Physical Energy (Truth):</span>
                <span className="font-mono text-emerald-300 font-bold">
                  {(activeInspectNode.residual * 1000).toFixed(2)} mJ ({activeInspectNode.truePercentage}%)
                </span>
              </div>
              <div className="flex justify-between items-center bg-[#0d111a] px-2 py-1 rounded">
                <span className="text-slate-400">Router Belief (DT):</span>
                <span className="font-mono text-cyan-300 font-bold">
                  {(activeInspectNode.believedEnergy * 1000).toFixed(2)} mJ ({activeInspectNode.beliefPercentage}%)
                </span>
              </div>
              <div className="flex justify-between items-center bg-[#0d111a] px-2 py-1 rounded">
                <span className="text-slate-400">Estimation Divergence:</span>
                <span className="font-mono text-amber-300 font-bold">
                  &plusmn;{(activeInspectNode.estimationError * 1000).toFixed(2)} mJ
                </span>
              </div>
              {activeInspectNode.beliefStd > 0 && (
                <div className="flex justify-between items-center bg-[#0d111a] px-2 py-1 rounded">
                  <span className="text-slate-400">Belief Uncertainty (σ):</span>
                  <span className="font-mono text-cyan-200">
                    &plusmn;{(activeInspectNode.beliefStd * 1000).toFixed(2)} mJ
                  </span>
                </div>
              )}
              <div className="grid grid-cols-2 gap-1.5 pt-1 text-[10px]">
                <div className="bg-[#0b0e16] p-1.5 rounded border border-[#191f2e]">
                  <span className="text-slate-400 block">Initial Charge:</span>
                  <span className="font-mono text-slate-200 font-bold">
                    {(activeInspectNode.initEnergy * 1000).toFixed(1)} mJ
                  </span>
                </div>
                <div className="bg-[#0b0e16] p-1.5 rounded border border-[#191f2e]">
                  <span className="text-slate-400 block">Solar Exposure:</span>
                  <span className="font-mono text-amber-300 font-bold flex items-center gap-1">
                    {activeInspectNode.isShaded ? <Cloud className="w-3 h-3 text-slate-400" /> : <Sun className="w-3 h-3 text-amber-400" />}
                    {(activeInspectNode.shadowMul * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="bg-[#0b0e16] p-1.5 rounded border border-[#191f2e]">
                  <span className="text-slate-400 block">Coordinates:</span>
                  <span className="font-mono text-slate-300">
                    ({activeInspectNode.x.toFixed(1)}, {activeInspectNode.y.toFixed(1)})
                  </span>
                </div>
                <div className="bg-[#0b0e16] p-1.5 rounded border border-[#191f2e]">
                  <span className="text-slate-400 block">Cluster:</span>
                  <span className="font-mono text-slate-300">
                    {activeInspectNode.isCH ? 'Leader' : `CH #${activeInspectNode.clusterId ?? 'None'}`}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Real-Time Live Network State Bar (Differentiates Every Node) */}
      <div className="p-2 bg-[#050608] border-t border-[#1b1d26] flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>State Counts:</span>
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#064e3b]/40 text-emerald-300 border border-[#10b981]/30">
            ⚡ Full (&gt;70%): {fullCount}
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#0e7490]/40 text-cyan-300 border border-[#06b6d4]/30">
            🟢 Good (40-70%): {goodCount}
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#b45309]/40 text-amber-300 border border-[#f59e0b]/30">
            🟡 Mod (20-40%): {modCount}
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#991b1b]/40 text-rose-300 border border-[#ef4444]/30">
            🔴 Low (&lt;20%): {lowCount}
          </span>
          {deadCount > 0 && (
            <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#1e2330] text-slate-400 border border-slate-600">
              💀 Dead: {deadCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
          <span className="flex items-center gap-1">
            <Sun className="w-3.5 h-3.5 text-amber-400" />
            <span>{sunlitCount} Sunlit</span>
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <Cloud className="w-3.5 h-3.5 text-slate-400" />
            <span>{shadedCount} Shaded</span>
          </span>
          <span>•</span>
          <span className="flex items-center gap-1 text-cyan-300">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>{activeRelayNodeIds.size} Relays</span>
          </span>
        </div>
      </div>
    </div>
  );
};
