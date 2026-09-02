import React, { useState, useEffect, useRef } from 'react';
import { Zap, Sun, Flame } from 'lucide-react';
import { SimulationResults, SimulationConfig, NodePosition } from '../types';

interface EnergyHeatmapViewProps {
  results: SimulationResults | null;
  config: SimulationConfig;
  currentRound?: number;
}

export const EnergyHeatmapView: React.FC<EnergyHeatmapViewProps> = ({
  results,
  config,
  currentRound = 0
}) => {
  const [metric, setMetric] = useState<'residual' | 'harvest' | 'consumption'>('residual');
  const [gridResolution] = useState<number>(30); // 30x30 interpolation grid
  const [showNodeOverlay, setShowNodeOverlay] = useState<boolean>(true);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  const areaSize = config.area || 100;
  const numNodes = config.nodes || 50;

  const roundIdx = results
    ? Math.min(currentRound, (results.detailed_data.energy_matrix.length || 1) - 1)
    : 0;

  const nodePositions: Record<string, NodePosition> = results?.detailed_data.node_positions || {};
  const energyMatrix = results?.detailed_data.energy_matrix;
  const shadowMultipliers = results?.detailed_data.node_shadow_multipliers || {};

  // Color mapping function (sober, muted palette)
  const getColorForNormalizedVal = (val: number, type: 'residual' | 'harvest' | 'consumption') => {
    const clamped = Math.max(0, Math.min(1, val));
    if (type === 'residual') {
      // 0 = Dark charcoal/brick, 0.5 = Ochre/slate, 1.0 = Muted steel blue
      if (clamped < 0.25) {
        const t = clamped / 0.25;
        return [Math.round(45 + 50 * t), 25, 25, 0.85]; // dark brick
      } else if (clamped < 0.6) {
        const t = (clamped - 0.25) / 0.35;
        return [Math.round(95 + 30 * t), Math.round(55 + 40 * t), 30, 0.85]; // ochre
      } else {
        const t = (clamped - 0.6) / 0.4;
        return [Math.round(125 * (1 - t) + 40 * t), Math.round(95 * (1 - t) + 85 * t), Math.round(30 * (1 - t) + 120 * t), 0.85]; // steel blue
      }
    } else if (type === 'harvest') {
      // Solar intensity: Dark charcoal -> Muted warm grey
      return [
        Math.round(20 + 130 * clamped),
        Math.round(24 + 110 * Math.pow(clamped, 1.2)),
        Math.round(30 + 60 * clamped),
        0.85
      ];
    } else {
      // Consumption: Muted dark slate -> Muted burnt sienna
      return [
        Math.round(25 + 120 * Math.pow(clamped, 0.9)),
        Math.round(30 + 40 * clamped),
        Math.round(40 + 20 * (1 - clamped)),
        0.85
      ];
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    // Prepare node values
    const nodeData: { x: number; y: number; val: number }[] = [];
    const maxCapacity = config.max_capacity || 1.0;

    for (let i = 0; i < numNodes; i++) {
      const pos = nodePositions[i] || { x: (i * 17) % areaSize, y: (i * 23) % areaSize };
      let nodeVal = 0;

      if (metric === 'residual') {
        const res = energyMatrix && energyMatrix[roundIdx] ? energyMatrix[roundIdx][i] : config.init_energy;
        nodeVal = res / maxCapacity;
      } else if (metric === 'harvest') {
        const shadow = shadowMultipliers[i] !== undefined ? shadowMultipliers[i] : 1.0;
        nodeVal = shadow;
      } else {
        // consumption
        const res0 = energyMatrix && energyMatrix[0] ? energyMatrix[0][i] : config.init_energy;
        const resNow = energyMatrix && energyMatrix[roundIdx] ? energyMatrix[roundIdx][i] : config.init_energy;
        nodeVal = Math.max(0, (res0 - resNow) / maxCapacity);
      }

      nodeData.push({
        x: (pos.x / areaSize) * width,
        y: (pos.y / areaSize) * height,
        val: nodeVal
      });
    }

    // Inverse Distance Weighting (IDW) 2D spatial interpolation
    const imgData = ctx.createImageData(width, height);
    const data = imgData.data;

    const p = 2;
    const epsilon = 1.0;

    const cellW = width / gridResolution;
    const cellH = height / gridResolution;

    for (let gx = 0; gx < gridResolution; gx++) {
      for (let gy = 0; gy < gridResolution; gy++) {
        const px = (gx + 0.5) * cellW;
        const py = (gy + 0.5) * cellH;

        let num = 0;
        let den = 0;

        for (const n of nodeData) {
          const distSq = (px - n.x) ** 2 + (py - n.y) ** 2;
          const w = 1 / (Math.pow(distSq + epsilon, p / 2));
          num += w * n.val;
          den += w;
        }

        const interpolatedVal = den > 0 ? num / den : 0;
        const [r, g, b, a] = getColorForNormalizedVal(interpolatedVal, metric);

        const startX = Math.floor(gx * cellW);
        const endX = Math.min(width, Math.floor((gx + 1) * cellW));
        const startY = Math.floor(gy * cellH);
        const endY = Math.min(height, Math.floor((gy + 1) * cellH));

        for (let y = startY; y < endY; y++) {
          for (let x = startX; x < endX; x++) {
            const idx = (y * width + x) * 4;
            data[idx] = r;
            data[idx + 1] = g;
            data[idx + 2] = b;
            data[idx + 3] = Math.round(a * 255);
          }
        }
      }
    }

    ctx.putImageData(imgData, 0, 0);

    // Draw Node overlays
    if (showNodeOverlay) {
      for (let i = 0; i < nodeData.length; i++) {
        const n = nodeData[i];
        ctx.beginPath();
        ctx.arc(n.x, n.y, 3.5, 0, 2 * Math.PI);
        ctx.fillStyle = '#cbd5e1';
        ctx.strokeStyle = '#090a0f';
        ctx.lineWidth = 1;
        ctx.fill();
        ctx.stroke();
      }

      // Draw Base station
      const bsCanvasX = ((config.bs_x ?? areaSize / 2) / areaSize) * width;
      const bsCanvasY = ((config.bs_y ?? areaSize / 2) / areaSize) * height;
      ctx.beginPath();
      ctx.rect(bsCanvasX - 5, bsCanvasY - 5, 10, 10);
      ctx.fillStyle = '#7f2d2d';
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 1.2;
      ctx.fill();
      ctx.stroke();
    }
  }, [results, currentRound, metric, gridResolution, showNodeOverlay, config, areaSize, numNodes, roundIdx]);

  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden space-y-3 p-4">
      {/* Top Header & Metric Filters */}
      <div className="bg-[#050608] border border-[#1b1d26] p-3 rounded flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-semibold text-slate-200">
            2D Spatial Energy Field & Contour Map
          </span>
          {results && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#101218] text-slate-300 border border-[#20232e]">
              Round {roundIdx}
            </span>
          )}
        </div>

        {/* Metric Selector Buttons */}
        <div className="flex items-center gap-2 text-xs">
          <div className="flex items-center bg-[#07080a] p-0.5 rounded border border-[#1c1e28]">
            <button
              onClick={() => setMetric('residual')}
              className={`px-2.5 py-1 rounded text-[11px] flex items-center gap-1.5 transition-colors ${
                metric === 'residual' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className="w-3 h-3" />
              <span>Residual Energy</span>
            </button>
            <button
              onClick={() => setMetric('harvest')}
              className={`px-2.5 py-1 rounded text-[11px] flex items-center gap-1.5 transition-colors ${
                metric === 'harvest' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sun className="w-3 h-3" />
              <span>Solar Exposure</span>
            </button>
            <button
              onClick={() => setMetric('consumption')}
              className={`px-2.5 py-1 rounded text-[11px] flex items-center gap-1.5 transition-colors ${
                metric === 'consumption' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Flame className="w-3 h-3" />
              <span>Depletion Rate</span>
            </button>
          </div>

          <button
            onClick={() => setShowNodeOverlay(!showNodeOverlay)}
            className={`px-2.5 py-1 rounded text-[11px] border transition-colors ${
              showNodeOverlay ? 'bg-[#181a24] border-[#2a2e3e] text-slate-100' : 'bg-[#07080a] border-[#1c1e28] text-slate-400 hover:text-slate-200'
            }`}
          >
            Node Dots: {showNodeOverlay ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Heatmap Canvas Container */}
      <div className="flex-1 bg-black border border-[#1b1d26] rounded flex items-center justify-center p-4 relative overflow-hidden">
        <canvas
          ref={canvasRef}
          width={500}
          height={500}
          className="rounded border border-[#1e202a] max-w-full max-h-[480px]"
        />

        {/* Gradient Legend Scale */}
        <div className="absolute bottom-6 right-6 bg-[#06070ae8] p-2.5 rounded border border-[#1e212c] text-[10px] space-y-1.5 w-44">
          <div className="font-semibold text-slate-300 flex justify-between">
            <span>
              {metric === 'residual' ? 'Battery %' : metric === 'harvest' ? 'Solar Multiplier' : 'Depleted Energy'}
            </span>
            <span className="font-mono text-slate-400">
              {metric === 'residual' ? '0% → 100%' : metric === 'harvest' ? '0% → 100%' : 'Low → High'}
            </span>
          </div>
          <div className="h-2.5 rounded overflow-hidden border border-[#1c1e28]">
            {metric === 'residual' ? (
              <div className="w-full h-full bg-gradient-to-r from-[#2d1919] via-[#5f4722] to-[#3a526d]" />
            ) : metric === 'harvest' ? (
              <div className="w-full h-full bg-gradient-to-r from-[#141822] via-[#4d4a3b] to-[#99927d]" />
            ) : (
              <div className="w-full h-full bg-gradient-to-r from-[#141822] via-[#543b35] to-[#8a4b3d]" />
            )}
          </div>
          <div className="flex justify-between text-slate-400 font-mono">
            <span>Min</span>
            <span>Max</span>
          </div>
        </div>
      </div>
    </div>
  );
};

