"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export interface TrendPoint {
  date: string;
  value: number;
}

export function TrendChart({
  points,
  unit,
  height = 220,
}: {
  points: TrendPoint[];
  unit?: string | null;
  height?: number;
}) {
  return (
    <div style={{ height }} role="img" aria-label={`Trend chart with ${points.length} data points`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 8, right: 12, bottom: 4, left: -8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
          <Tooltip formatter={(v) => [`${v}${unit ? " " + unit : ""}`, "Value"]} />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#2a706d"
            strokeWidth={2}
            dot={{ r: 3 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function TrendArrow({ direction }: { direction: string }) {
  const map: Record<string, { char: string; tone: string; label: string }> = {
    increasing: { char: "↑", tone: "text-amber-600", label: "increasing" },
    decreasing: { char: "↓", tone: "text-sky-600", label: "decreasing" },
    stable: { char: "→", tone: "text-emerald-600", label: "stable" },
    sudden_change: { char: "⇈", tone: "text-red-600", label: "sudden change" },
    insufficient_data: { char: "·", tone: "text-slate-400", label: "insufficient data" },
  };
  const item = map[direction] ?? map.insufficient_data;
  return (
    <span className={`font-semibold ${item.tone}`} title={item.label}>
      <span aria-hidden="true">{item.char}</span>
      <span className="sr-only">{item.label}</span>
    </span>
  );
}
