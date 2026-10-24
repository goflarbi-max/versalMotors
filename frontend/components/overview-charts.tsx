"use client";

import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { BranchRevenueRecord, formatCompactGhs, formatMonth, ModelMarginRecord, RevenueTrendRecord } from "@/lib/overview";

const axis = { fill: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-app)" };
const tooltipStyle = { border: "1px solid var(--border)", borderRadius: 12, background: "var(--surface)", color: "var(--text)", fontFamily: "var(--font-app)" };

export function RevenueTrendChart({ data }: { data: RevenueTrendRecord[] }) {
  return <div className="chart-canvas" aria-label={`Revenue trend chart with ${data.length} periods`}>
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 12, right: 12, left: 8, bottom: 4 }}>
        <defs><linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#16c060" stopOpacity={0.28}/><stop offset="95%" stopColor="#16c060" stopOpacity={0.02}/></linearGradient></defs>
        <CartesianGrid vertical strokeDasharray="4 4" stroke="var(--chart-grid)" horizontal={false}/>
        <XAxis dataKey="period" tickFormatter={formatMonth} tick={axis} tickLine={false} axisLine={false}/>
        <YAxis tickFormatter={formatCompactGhs} tick={axis} tickLine={false} axisLine={false} width={74}/>
        <Tooltip formatter={(value) => [formatCompactGhs(Number(value)), "Revenue"]} labelFormatter={(label) => formatMonth(String(label))} contentStyle={tooltipStyle}/>
        <Area type="monotone" dataKey="revenue" stroke="#16c060" strokeWidth={2.5} fill="url(#revenueFill)" dot={false} activeDot={{ r: 4 }}/>
      </AreaChart>
    </ResponsiveContainer>
  </div>;
}

export function BranchRevenueChart({ data }: { data: BranchRevenueRecord[] }) {
  return <div className="chart-canvas chart-tall" aria-label={`Revenue by branch chart with ${data.length} branches`}>
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 20, left: 22, bottom: 4 }}>
        <CartesianGrid horizontal={false} strokeDasharray="4 4" stroke="var(--chart-grid)"/>
        <XAxis type="number" tickFormatter={formatCompactGhs} tick={axis} tickLine={false} axisLine={false}/>
        <YAxis type="category" dataKey="branch" tick={axis} tickLine={false} axisLine={false} width={82}/>
        <Tooltip formatter={(value) => [formatCompactGhs(Number(value)), "Revenue"]} contentStyle={tooltipStyle}/>
        <Bar dataKey="revenue" fill="#16c060" radius={[0, 7, 7, 0]} maxBarSize={24}/>
      </BarChart>
    </ResponsiveContainer>
  </div>;
}

export function ModelMarginChart({ data }: { data: ModelMarginRecord[] }) {
  return <div className="chart-canvas" aria-label={`Gross margin by model chart with ${data.length} models`}>
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 20, left: 22, bottom: 4 }}>
        <CartesianGrid horizontal={false} strokeDasharray="4 4" stroke="var(--chart-grid)"/>
        <XAxis type="number" tickFormatter={formatCompactGhs} tick={axis} tickLine={false} axisLine={false}/>
        <YAxis type="category" dataKey="model" tick={axis} tickLine={false} axisLine={false} width={94}/>
        <Tooltip formatter={(value) => [formatCompactGhs(Number(value)), "Gross margin"]} contentStyle={tooltipStyle}/>
        <Bar dataKey="gross_margin" fill="#3db2a0" radius={[0, 7, 7, 0]} maxBarSize={28}/>
      </BarChart>
    </ResponsiveContainer>
  </div>;
}
