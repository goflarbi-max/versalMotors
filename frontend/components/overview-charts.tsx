"use client";

import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { BranchRevenueRecord, formatCompactGhs, formatMonth, ModelMarginRecord, RevenueTrendRecord } from "@/lib/overview";

const axis = { fill: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-app)" };
const tooltipStyle = { border: "1px solid var(--border)", borderRadius: 12, background: "var(--surface)", color: "var(--text)", fontFamily: "var(--font-app)" };
const legendStyle = { color: "var(--text-muted)", fontFamily: "var(--font-app)", fontSize: 12 };
const formatFullGhs = (value: number) => `GHS ${value.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;

export function RevenueTrendChart({ data }: { data: RevenueTrendRecord[] }) {
  return <div className="chart-canvas" aria-label={`Revenue trend chart with ${data.length} periods`}>
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 12, right: 18, left: 18, bottom: 24 }}>
        <defs><linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#16c060" stopOpacity={0.28}/><stop offset="95%" stopColor="#16c060" stopOpacity={0.02}/></linearGradient></defs>
        <CartesianGrid vertical strokeDasharray="4 4" stroke="var(--chart-grid)" horizontal={false}/>
        <XAxis dataKey="period" tickFormatter={formatMonth} tick={axis} tickLine={false} axisLine={false} label={{ value: "Month", position: "insideBottom", offset: -14, style: axis }}/>
        <YAxis tickFormatter={formatCompactGhs} tick={axis} tickLine={false} axisLine={false} width={82} label={{ value: "Revenue (GHS)", angle: -90, position: "insideLeft", offset: -8, style: axis }}/>
        <Tooltip formatter={(value) => [formatFullGhs(Number(value)), "Revenue"]} labelFormatter={(label) => formatMonth(String(label))} contentStyle={tooltipStyle}/>
        <Legend verticalAlign="top" align="right" iconType="square" wrapperStyle={legendStyle}/>
        <Area name="Revenue" type="monotone" dataKey="revenue" stroke="#16c060" strokeWidth={2.4} fill="url(#revenueFill)" dot={false} activeDot={{ r: 4 }}/>
      </AreaChart>
    </ResponsiveContainer>
  </div>;
}

export function BranchRevenueChart({ data }: { data: BranchRevenueRecord[] }) {
  return <div className="chart-canvas chart-tall" aria-label={`Revenue by branch chart with ${data.length} branches`}>
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" barGap={0} barCategoryGap="28%" margin={{ top: 12, right: 20, left: 30, bottom: 24 }}>
        <CartesianGrid horizontal={false} strokeDasharray="4 4" stroke="var(--chart-grid)"/>
        <XAxis type="number" tickFormatter={formatCompactGhs} tick={axis} tickLine={false} axisLine={false} label={{ value: "Revenue (GHS)", position: "insideBottom", offset: -14, style: axis }}/>
        <YAxis type="category" dataKey="branch" tick={axis} tickLine={false} axisLine={false} width={82} label={{ value: "Branch", angle: -90, position: "insideLeft", offset: -18, style: axis }}/>
        <Tooltip formatter={(value) => [formatFullGhs(Number(value)), "Revenue"]} contentStyle={tooltipStyle}/>
        <Legend verticalAlign="top" align="right" iconType="square" wrapperStyle={legendStyle}/>
        <Bar name="Revenue" dataKey="revenue" fill="#16c060" radius={[0, 6, 6, 0]} maxBarSize={24}/>
      </BarChart>
    </ResponsiveContainer>
  </div>;
}

export function ModelMarginChart({ data }: { data: ModelMarginRecord[] }) {
  return <div className="chart-canvas" aria-label={`Gross margin by model chart with ${data.length} models`}>
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" barGap={0} barCategoryGap="28%" margin={{ top: 12, right: 20, left: 30, bottom: 24 }}>
        <CartesianGrid horizontal={false} strokeDasharray="4 4" stroke="var(--chart-grid)"/>
        <XAxis type="number" tickFormatter={formatCompactGhs} tick={axis} tickLine={false} axisLine={false} label={{ value: "Gross margin (GHS)", position: "insideBottom", offset: -14, style: axis }}/>
        <YAxis type="category" dataKey="model" tick={axis} tickLine={false} axisLine={false} width={94} label={{ value: "Model", angle: -90, position: "insideLeft", offset: -18, style: axis }}/>
        <Tooltip formatter={(value) => [formatFullGhs(Number(value)), "Gross margin"]} contentStyle={tooltipStyle}/>
        <Legend verticalAlign="top" align="right" iconType="square" wrapperStyle={legendStyle}/>
        <Bar name="Gross margin" dataKey="gross_margin" fill="#16c060" radius={[0, 6, 6, 0]} maxBarSize={28}/>
      </BarChart>
    </ResponsiveContainer>
  </div>;
}
