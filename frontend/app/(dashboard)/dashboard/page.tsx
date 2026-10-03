'use strict';
'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Sparkles,
  Play,
  Upload,
  MessageSquare,
  Award,
  Zap,
  TrendingUp,
  Brain,
  FileText,
  LineChart,
  Inbox,
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { analyticsService } from '@/services/analytics';
import { useAuthStore } from '@/store';

export default function Dashboard() {
  const [data, setData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const { user } = useAuthStore();

  React.useEffect(() => {
    async function loadData() {
      try {
        const summary = await analyticsService.getDashboardSummary();
        setData(summary);
      } catch (_) {
        // Strict empty fallbacks if server/database is down or empty
        setData({
          user_name: user?.full_name || 'Candidate',
          active_profile: user?.active_profile_name || 'default',
          profile_details: {
            target_role: user?.profiles?.[user?.active_profile_name]?.target_role || 'Software Engineer',
            experience_level: user?.profiles?.[user?.active_profile_name]?.experience_level || 'Not Configured',
          },
          stats: {
            average_score: 0.0,
            highest_score: 0.0,
            total_interviews: 0,
            completed_interviews: 0,
            completion_rate: 0,
          },
          recent_progress: [],
        });
      }
      finally {
        setLoading(false);
      }
    }
    loadData();
  }, [user]);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 300, damping: 24 } },
  };

  if (loading || !data) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center space-y-4">
        <div className="h-8 w-8 border-4 border-accent-primary border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-text-secondary">Loading your workspace intelligence...</span>
      </div>
    );
  }

  const averageScorePercent = Math.round((data.stats.average_score / 10) * 100);
  const hasInterviews = data.stats.total_interviews > 0;

  const kpis = [
    { label: 'Interview Rating', value: hasInterviews ? `${data.stats.average_score}/10` : '0/10', trend: 'Average', color: 'text-accent-primary', data: data.recent_progress || [] },
    { label: 'Highest Score', value: hasInterviews ? `${data.stats.highest_score}/10` : '0/10', trend: 'Personal Best', color: 'text-success', data: hasInterviews ? [data.stats.highest_score] : [] },
    { label: 'Total Practice Runs', value: String(data.stats.total_interviews), trend: 'Sessions', color: 'text-accent-secondary', data: hasInterviews ? [data.stats.total_interviews] : [] },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8 max-w-7xl mx-auto"
    >
      {/* Personalized Greeting Card */}
      <motion.div variants={itemVariants}>
        <div className="relative overflow-hidden rounded-[26px] bg-gradient-to-r from-accent-primary/10 to-accent-secondary/5 border border-border-custom p-8 text-left">
          {/* Ambient Glow */}
          <div className="absolute -top-12 -right-12 w-64 h-64 bg-accent-primary/15 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
            <div>
              <div className="flex items-center gap-2 text-accent-primary font-bold text-sm mb-1.5 uppercase tracking-wider">
                <Sparkles className="h-4.5 w-4.5" />
                <span>Practice. Improve. Get Hired.</span>
              </div>
              <h1 className="text-3xl font-bold tracking-tight text-text-primary">
                Good Afternoon, {data.user_name}
              </h1>
              <p className="text-sm text-text-secondary mt-1.5 max-w-md">
                {hasInterviews
                  ? `You have completed ${data.stats.completed_interviews} practice runs. Let's continue simulating active role scenarios.`
                  : 'Welcome to your mock interview intelligence workspace. Begin by configuring your first practice session.'}
              </p>
            </div>

            {/* Circular AI Scorecard */}
            <div className="flex items-center gap-4 bg-surface-primary/60 border border-border-custom px-6 py-4 rounded-2xl">
              <div className="relative h-16 w-16 flex items-center justify-center">
                <svg className="absolute transform -rotate-90 w-16 h-16">
                  <circle cx="32" cy="32" r="28" stroke="var(--border)" strokeWidth="4" fill="transparent" />
                  <circle cx="32" cy="32" r="28" stroke="var(--accent-primary)" strokeWidth="4" fill="transparent"
                    strokeDasharray={175} strokeDashoffset={175 - (175 * averageScorePercent) / 100} strokeLinecap="round" />
                </svg>
                <span className="text-lg font-bold text-text-primary">{averageScorePercent}%</span>
              </div>
              <div className="text-left">
                <span className="text-[10px] text-text-muted uppercase font-bold block">AI Readiness Score</span>
                <span className="text-sm font-semibold text-text-primary">
                  {data.profile_details?.target_role || 'Not Configured'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Quick Action Hubs */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link href="/practice" className="block">
          <Card className="flex items-center gap-4 hover:border-accent-primary transition-all p-5 text-left cursor-pointer">
            <div className="h-11 w-11 bg-accent-primary/10 rounded-xl flex items-center justify-center text-accent-primary">
              <Play className="h-5.5 w-5.5 fill-current" />
            </div>
            <div>
              <span className="font-semibold text-text-primary block">Start Mock Session</span>
              <span className="text-xs text-text-muted">Simulate a live loop</span>
            </div>
          </Card>
        </Link>

        <Link href="/resume" className="block">
          <Card className="flex items-center gap-4 hover:border-accent-secondary transition-all p-5 text-left cursor-pointer">
            <div className="h-11 w-11 bg-accent-secondary/10 rounded-xl flex items-center justify-center text-accent-secondary">
              <Upload className="h-5.5 w-5.5" />
            </div>
            <div>
              <span className="font-semibold text-text-primary block">Upload Resume</span>
              <span className="text-xs text-text-muted">Audit skills and keywords</span>
            </div>
          </Card>
        </Link>

        <Link href="/journey" className="block">
          <Card className="flex items-center gap-4 hover:border-success transition-all p-5 text-left cursor-pointer">
            <div className="h-11 w-11 bg-success/10 rounded-xl flex items-center justify-center text-success">
              <MessageSquare className="h-5.5 w-5.5" />
            </div>
            <div>
              <span className="font-semibold text-text-primary block">Review Feedback</span>
              <span className="text-xs text-text-muted">Study model solutions</span>
            </div>
          </Card>
        </Link>

        <Link href="/performance" className="block">
          <Card className="flex items-center gap-4 hover:border-warning transition-all p-5 text-left cursor-pointer">
            <div className="h-11 w-11 bg-warning/10 rounded-xl flex items-center justify-center text-warning">
              <TrendingUp className="h-5.5 w-5.5" />
            </div>
            <div>
              <span className="font-semibold text-text-primary block">Analytics Metrics</span>
              <span className="text-xs text-text-muted">Track chronological path</span>
            </div>
          </Card>
        </Link>
      </motion.div>

      {/* KPI Stats widgets with mini sparklines */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpis.map((kpi) => (
          <Card key={kpi.label} className="p-6 text-left">
            <span className="text-xs text-text-muted block font-semibold">{kpi.label}</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className={`text-3xl font-bold ${kpi.color}`}>{kpi.value}</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-success/10 text-success">
                {kpi.trend}
              </span>
            </div>

            {/* Sparkline Graphic */}
            <div className="h-10 mt-4 flex items-end">
              {kpi.data.length > 1 ? (
                <svg className="w-full h-full" viewBox="0 0 100 30" preserveAspectRatio="none">
                  <path
                    d={`M 0 30 ${kpi.data.map((val: number, idx: number) => `L ${(idx * 100) / (kpi.data.length - 1)} ${30 - (Number(val) * 2.5)}`).join(' ')}`}
                    fill="none"
                    stroke="var(--accent-primary)"
                    strokeWidth="2"
                  />
                </svg>
              ) : (
                <span className="text-xs text-text-muted font-mono select-none">No timeline trend data yet</span>
              )}
            </div>
          </Card>
        ))}
      </motion.div>

      {/* Split layout: AI Insights and Activity logs */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Col: Today's AI Recommendation */}
        <div className="lg:col-span-7 space-y-6">
          <h2 className="text-xl font-bold text-text-primary text-left">Today's AI Insights</h2>
          <Card className="p-6 text-left relative overflow-hidden bg-surface-primary border-border-hover">
            <div className="flex items-start gap-4">
              <div className="h-10 w-10 bg-accent-primary/10 border border-accent-primary/20 rounded-xl flex items-center justify-center text-accent-primary shrink-0">
                <Brain className="h-5 w-5" />
              </div>
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-text-primary">System Design Preparation Recommendation</h3>
                  <p className="text-sm text-text-secondary leading-relaxed mt-1.5">
                    {hasInterviews
                      ? 'Based on your previous performance records, Granite AI recommends continuing to configure Kubernetes horizontal pod autoscaling and testing Redis database cluster latency solutions.'
                      : 'Please complete your first mock interview simulation session to generate automated evaluation tips and Granite AI instructions.'}
                  </p>
                </div>
                <div className="flex gap-2">
                  <span className="text-xs font-semibold px-2.5 py-1 bg-surface-secondary border border-border-custom rounded-lg text-text-secondary">Track: Architecture</span>
                  <span className="text-xs font-semibold px-2.5 py-1 bg-surface-secondary border border-border-custom rounded-lg text-text-secondary">Target Grade: &gt; 8.5</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Col: Recent Activity timeline */}
        <div className="lg:col-span-5 space-y-6">
          <h2 className="text-xl font-bold text-text-primary text-left">Recent Activities</h2>
          <Card className="p-6 space-y-4 text-left">
            {hasInterviews ? (
              <div className="space-y-4">
                <div className="flex items-start gap-3 border-b border-border-custom pb-3.5">
                  <div className="h-8 w-8 bg-success/15 rounded-lg flex items-center justify-center text-success shrink-0 mt-0.5">
                    <Award className="h-4 w-4" />
                  </div>
                  <div>
                    <span className="font-semibold text-text-primary text-sm block">System Design Practice Completed</span>
                    <span className="text-xs text-text-muted block mt-0.5">Mock session successfully graded.</span>
                  </div>
                </div>

                <div className="flex items-start gap-3 border-b border-border-custom pb-3.5">
                  <div className="h-8 w-8 bg-accent-secondary/15 rounded-lg flex items-center justify-center text-accent-secondary shrink-0 mt-0.5">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <span className="font-semibold text-text-primary text-sm block">Resume parsed</span>
                    <span className="text-xs text-text-muted block mt-0.5">Skills and matching index calculated.</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-6 text-center space-y-3">
                <Inbox className="h-8 w-8 text-text-muted" />
                <span className="text-xs text-text-muted block">No activity logs recorded.</span>
              </div>
            )}
          </Card>
        </div>

      </motion.div>
    </motion.div>
  );
}
