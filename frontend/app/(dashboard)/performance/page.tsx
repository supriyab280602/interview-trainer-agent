'use client';

import * as React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
} from 'recharts';
import { Card } from '@/components/ui/card';
import { TrendingUp, Award, Brain, Clock } from 'lucide-react';

const trendData = [
  { name: 'Run 1', score: 6.5 },
  { name: 'Run 2', score: 7.0 },
  { name: 'Run 3', score: 6.8 },
  { name: 'Run 4', score: 7.5 },
  { name: 'Run 5', score: 8.2 },
  { name: 'Run 6', score: 8.4 },
];

const skillData = [
  { subject: 'System Design', A: 85, fullMark: 100 },
  { subject: 'Coding Syntax', A: 78, fullMark: 100 },
  { subject: 'Behavioral', A: 90, fullMark: 100 },
  { subject: 'STAR method', A: 92, fullMark: 100 },
  { subject: 'Communication', A: 84, fullMark: 100 },
];

const categoryData = [
  { name: 'Technical', count: 6 },
  { name: 'Behavioral', count: 4 },
  { name: 'System Design', count: 3 },
  { name: 'HR', count: 2 },
];

export default function PerformanceIntelligence() {
  return (
    <div className="max-w-7xl mx-auto space-y-8 text-left">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">Performance Intelligence</h1>
        <p className="text-sm text-text-secondary">Chronological audit metrics compiled from your practice logs.</p>
      </div>

      {/* KPI Overviews row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-5 flex items-center gap-4">
          <div className="h-10 w-10 bg-accent-primary/10 rounded-xl flex items-center justify-center text-accent-primary">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <span className="text-xs text-text-muted block">Avg Rating</span>
            <span className="text-xl font-bold text-text-primary">8.4 / 10</span>
          </div>
        </Card>

        <Card className="p-5 flex items-center gap-4">
          <div className="h-10 w-10 bg-accent-secondary/10 rounded-xl flex items-center justify-center text-accent-secondary">
            <Award className="h-5 w-5" />
          </div>
          <div>
            <span className="text-xs text-text-muted block">Best Session</span>
            <span className="text-xl font-bold text-text-primary">9.1 / 10</span>
          </div>
        </Card>

        <Card className="p-5 flex items-center gap-4">
          <div className="h-10 w-10 bg-success/10 rounded-xl flex items-center justify-center text-success">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <span className="text-xs text-text-muted block">Total Hours</span>
            <span className="text-xl font-bold text-text-primary">12.5 hrs</span>
          </div>
        </Card>

        <Card className="p-5 flex items-center gap-4">
          <div className="h-10 w-10 bg-warning/10 rounded-xl flex items-center justify-center text-warning">
            <Clock className="h-5 w-5" />
          </div>
          <div>
            <span className="text-xs text-text-muted block">Completes</span>
            <span className="text-xl font-bold text-text-primary">15 Runs</span>
          </div>
        </Card>
      </div>

      {/* Recharts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Trend Area Chart */}
        <div className="lg:col-span-8">
          <Card className="p-6 space-y-4">
            <h3 className="font-bold text-text-primary text-lg">Readiness Trend Timeline</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-primary)" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="var(--accent-primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 10]} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--surface-primary)',
                      borderColor: 'var(--border)',
                      borderRadius: '12px',
                      color: 'var(--text-primary)',
                    }}
                  />
                  <Area type="monotone" dataKey="score" stroke="var(--accent-primary)" strokeWidth={2} fillOpacity={1} fill="url(#colorScore)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Skill Radar Chart */}
        <div className="lg:col-span-4">
          <Card className="p-6 space-y-4">
            <h3 className="font-bold text-text-primary text-lg">Radar Competencies</h3>
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={skillData}>
                  <PolarGrid stroke="var(--border)" />
                  <PolarAngleAxis dataKey="subject" stroke="var(--text-secondary)" fontSize={10} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="var(--border)" />
                  <Radar name="Candidate" dataKey="A" stroke="var(--accent-secondary)" fill="var(--accent-secondary)" fillOpacity={0.15} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </div>

      {/* Category distribution bar chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-6">
          <Card className="p-6 space-y-4">
            <h3 className="font-bold text-text-primary text-lg">Mock Category distribution</h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData}>
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--surface-primary)',
                      borderColor: 'var(--border)',
                      borderRadius: '12px',
                    }}
                  />
                  <Bar dataKey="count" fill="var(--accent-primary)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </div>

    </div>
  );
}
