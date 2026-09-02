import React, { useState, useRef } from 'react';
import { NodePosition, SimulationConfig, SimulationResults } from '../types';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Eye,
  Zap,
  Radio,
  Share2,
  Info
} from 'lucide-react';

interface NetworkTopologyViewProps {
  results: SimulationResults | null;
  config: SimulationConfig;
  currentRound?: number;
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
  const [showClusters, setShowClusters] = useState<boolean>(true);
  const [showRoutes, setShowRoutes] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(false);

  const containerRef = useRef<HTMLDivElement>(null);

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

  const currentCHs = chHistory && chHistory[roundIdx] ? chHistory[roundIdx] : [];
  const currentRoutes = routesHistory && routesHistory[roundIdx] ? routesHistory[roundIdx] : {};
  const currentAssignments = clusterAssignments && clusterAssignments[roundIdx] ? clusterAssignments[roundIdx] : {};

  // Base station coordinates
  const bsX = config.bs_x !== undefined ? config.bs_x : areaSize / 2;
  const bsY = config.bs_y !== undefined ? config.bs_y : areaSize / 2;

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

  // Build node data for rendering
  const nodes = [];
  for (let i = 0; i < numNodes; i++) {
    const pos = nodePositions[i] || {
      x: (i * 17) % areaSize,
      y: (i * 23) % areaSize
    };
    const residual = energyMatrix && energyMatrix[roundIdx] ? energyMatrix[roundIdx][i] : config.init_energy;
    const isAlive = residual > 1e-6;
    const isCH = currentCHs.includes(i);
    const clusterId = currentAssignments[i] !== undefined ? currentAssignments[i] : (isCH ? i : null);
    const shadowMul = shadowMultipliers[i] !== undefined ? shadowMultipliers[i] : 1.0;
    const maxEnergy = config.max_capacity || 1.0;
    const energyRatio = Math.max(0, Math.min(1, residual / maxEnergy));

    nodes.push({
      id: i,
      x: pos.x,
      y: pos.y,
      residual,
      energyRatio,
      isAlive,
      isCH,
      clusterId,
      shadowMul
    });
  }

  const activeHoverNode = hoveredNodeId !== null ? nodes.find(n => n.id === hoveredNodeId) : null;

  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden relative">
      {/* Top Toolbar */}
      <div className="p-3 bg-[#050608] border-b border-[#1b1d26] flex flex-wrap items-center justify-between gap-2 z-10">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold text-slate-200">
              Network Topology ({areaSize}m × {areaSize}m)
            </span>
          </div>
          {results && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#101218] text-slate-300 border border-[#20232e]">
              Round {roundIdx} / {config.rounds}
            </span>
          )}
        </div>

        {/* View toggles & zoom controls */}
        <div className="flex items-center gap-2 text-xs">
          <div className="flex items-center bg-[#07080a] p-0.5 rounded border border-[#1c1e28]">
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
              onClick={() => setShowRoutes(!showRoutes)}
              className={`px-2 py-1 rounded text-[11px] flex items-center gap-1 transition-colors ${
                showRoutes ? 'bg-[#181a24] text-slate-100 font-medium border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle Multi-Hop Routing Paths"
            >
              <Zap className="w-3 h-3" />
              <span>Routes</span>
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
          </div>

          <div className="flex items-center bg-[#07080a] p-0.5 rounded border border-[#1c1e28]">
            <button
              onClick={() => setZoom(prev => Math.min(prev * 1.2, 4))}
              className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-[#14161f]"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoom(prev => Math.max(prev * 0.8, 0.5))}
              className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-[#14161f]"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={resetZoom}
              className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-[#14161f]"
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
        className="flex-1 w-full h-[540px] bg-black relative overflow-hidden cursor-grab active:cursor-grabbing select-none"
      >
        <svg
          className="w-full h-full"
          viewBox={`0 0 600 600`}
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Grid Pattern */}
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#12141c" strokeWidth="0.75" />
            </pattern>
            {/* Shadow Zone Pattern */}
            <pattern id="shadowHatch" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
              <line x1="0" y1="0" x2="0" y2="8" stroke="#171a24" strokeWidth="2" opacity="0.7" />
            </pattern>
          </defs>

          <g transform={`translate(${pan.x + 300}, ${pan.y + 300}) scale(${zoom}) translate(-300, -300)`}>
            {/* Background Grid */}
            <rect x="0" y="0" width="600" height="600" fill="url(#grid)" />
            <rect x="0" y="0" width="600" height="600" fill="none" stroke="#1f2230" strokeWidth="1.2" />

            {/* If shadowed solar regime, draw shadow zone */}
            {config.harvesting_profile === 'shadowed_solar' && (
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
                  stroke="#333b4e"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  opacity="0.8"
                />
                <text
                  x="10"
                  y="20"
                  fill="#7a889b"
                  fontSize="11"
                  fontFamily="monospace"
                  opacity="0.9"
                >
                  [SHADOW ZONE • ~30% SOLAR IRRADIANCE]
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
                  stroke="#3f4758"
                  strokeWidth="0.8"
                  strokeDasharray="2 3"
                  opacity="0.4"
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

                pathSegments.push(
                  <g key={`route-${chId}-${u}-${v}-${idx}`}>
                    <line
                      x1={uX}
                      y1={uY}
                      x2={vX}
                      y2={vY}
                      stroke="#426b57"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      opacity="0.9"
                    />
                    <circle
                      cx={(uX + vX) / 2}
                      cy={(uY + vY) / 2}
                      r="1.8"
                      fill="#5e8c75"
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
                  <rect
                    x="-9"
                    y="-9"
                    width="18"
                    height="18"
                    rx="2"
                    fill="#6e2525"
                    stroke="#991b1b"
                    strokeWidth="1.2"
                  />
                  <polygon points="0,-5 -5,4 5,4" fill="#f8fafc" />
                  <text
                    y="18"
                    textAnchor="middle"
                    fill="#cbd5e1"
                    fontSize="10"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    BS ({bsX.toFixed(0)},{bsY.toFixed(0)})
                  </text>
                </g>
              );
            })()}

            {/* Sensor Nodes */}
            {nodes.map((node) => {
              const cx = (node.x / areaSize) * 600;
              const cy = (node.y / areaSize) * 600;
              const isHovered = hoveredNodeId === node.id;

              // Color based on role and energy
              let nodeColor = '#3e4f66'; // active member
              if (!node.isAlive) {
                nodeColor = '#242833'; // dead
              } else if (node.isCH) {
                nodeColor = '#925807'; // Cluster Head ochre
              } else if (node.energyRatio < 0.2) {
                nodeColor = '#7a2e2e'; // critical brick red
              } else if (node.energyRatio < 0.5) {
                nodeColor = '#735706'; // low battery mustard
              } else {
                nodeColor = '#3e4f66';
              }

              return (
                <g
                  key={`node-${node.id}`}
                  transform={`translate(${cx}, ${cy})`}
                  onMouseEnter={() => setHoveredNodeId(node.id)}
                  onMouseLeave={() => setHoveredNodeId(null)}
                  className="cursor-pointer"
                >
                  {/* Hover ring */}
                  {isHovered && (
                    <circle
                      r="12"
                      fill="none"
                      stroke="#94a3b8"
                      strokeWidth="1.2"
                      strokeDasharray="2 2"
                    />
                  )}

                  {/* Battery Percentage Outer Ring */}
                  {node.isAlive && (
                    <circle
                      r="6.5"
                      fill="none"
                      stroke="#141720"
                      strokeWidth="1.8"
                    />
                  )}
                  {node.isAlive && (
                    <circle
                      r="6.5"
                      fill="none"
                      stroke={nodeColor}
                      strokeWidth="1.8"
                      strokeDasharray={`${node.energyRatio * 40.8} 40.8`}
                      strokeLinecap="round"
                      transform="rotate(-90)"
                    />
                  )}

                  {/* Center Node Core */}
                  <circle
                    r={node.isCH ? 5 : 4}
                    fill={nodeColor}
                    stroke="#000000"
                    strokeWidth="1"
                  />

                  {/* Node ID label */}
                  {(showLabels || isHovered || node.isCH) && (
                    <text
                      y={node.isCH ? -9 : -7}
                      textAnchor="middle"
                      fill={node.isCH ? '#d97706' : '#94a3b8'}
                      fontSize={node.isCH ? '10' : '9'}
                      fontWeight={node.isCH ? 'bold' : 'normal'}
                      fontFamily="monospace"
                    >
                      {node.isCH ? `CH-${node.id}` : `N${node.id}`}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-[#06070ae8] p-2.5 rounded border border-[#1e212c] text-[10px] space-y-1.5 pointer-events-none">
          <div className="font-semibold text-slate-300 flex items-center gap-1.5 pb-1 border-b border-[#1b1d26]">
            <Info className="w-3 h-3 text-slate-400" />
            <span>Legend</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-[#6e2525] inline-block"></span>
              <span className="text-slate-300">Base Station</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#925807] inline-block"></span>
              <span className="text-slate-300">Cluster Head</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#3e4f66] inline-block"></span>
              <span className="text-slate-300">Active Sensor</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#242833] inline-block"></span>
              <span className="text-slate-400">Depleted</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 bg-[#426b57] inline-block"></span>
              <span className="text-slate-300">Multi-Hop Path</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 bg-[#3f4758] border-b border-dotted inline-block"></span>
              <span className="text-slate-300">Cluster Link</span>
            </div>
          </div>
        </div>

        {/* Hover Node Tooltip Card */}
        {activeHoverNode && (
          <div className="absolute top-3 right-3 bg-[#07080b] p-3 rounded border border-[#222634] text-xs w-60 z-20 space-y-1.5">
            <div className="flex items-center justify-between pb-1 border-b border-[#1b1d26]">
              <span className="font-semibold font-mono text-slate-200">
                Node #{activeHoverNode.id} {activeHoverNode.isCH && <span className="text-amber-500">(CH)</span>}
              </span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                activeHoverNode.isAlive ? 'bg-[#0f1f17] text-[#86efac] border border-[#1b3d29]' : 'bg-[#200f0f] text-[#fca5a5] border border-[#3d1818]'
              }`}>
                {activeHoverNode.isAlive ? 'ALIVE' : 'DEAD'}
              </span>
            </div>

            <div className="space-y-1 text-[11px] text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Position:</span>
                <span className="font-mono">({activeHoverNode.x.toFixed(1)}m, {activeHoverNode.y.toFixed(1)}m)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Residual Energy:</span>
                <span className="font-mono text-slate-200">
                  {(activeHoverNode.residual * 1000).toFixed(2)} mJ / {(config.max_capacity * 1000).toFixed(0)} mJ
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Battery Level:</span>
                <span className="font-mono text-slate-200 font-semibold">
                  {(activeHoverNode.energyRatio * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Role & Cluster:</span>
                <span className="font-mono text-slate-200">
                  {activeHoverNode.isCH ? 'Cluster Head' : `Member of CH #${activeHoverNode.clusterId ?? 'None'}`}
                </span>
              </div>
              {config.harvesting_profile === 'shadowed_solar' && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Solar Exposure:</span>
                  <span className="font-mono text-slate-300">
                    {(activeHoverNode.shadowMul * 100).toFixed(0)}% ({activeHoverNode.shadowMul < 0.5 ? 'Shaded' : 'Sunlit'})
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

