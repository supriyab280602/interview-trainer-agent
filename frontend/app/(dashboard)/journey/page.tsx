'use strict';
'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, Clock, Award, ChevronDown, ChevronUp, Download, Inbox } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { interviewService } from '@/services/interview';

function JourneyItem({ item }: { item: any }) {
  const [expanded, setExpanded] = React.useState(false);

  return (
    <Card className="p-6 text-left relative overflow-hidden transition-all">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-accent-primary/10 text-accent-primary uppercase">
            {item.interview_type || 'General'}
          </span>
          <h3 className="font-bold text-text-primary text-lg mt-1">
            {item.profile_name || 'Interview Session'}
          </h3>
          <div className="flex items-center gap-4 text-xs text-text-muted mt-1">
            <span className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" /> {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" /> {item.length || 5} Questions
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-surface-secondary border border-border-custom px-4 py-2 rounded-xl text-center">
            <span className="text-[10px] text-text-muted uppercase block font-bold">Grade</span>
            <span className="text-lg font-bold text-success">
              {item.overall_score !== undefined ? `${item.overall_score}/10` : 'Pending'}
            </span>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 rounded-xl hover:bg-surface-secondary text-text-secondary hover:text-text-primary transition-colors cursor-pointer border border-border-custom"
          >
            {expanded ? <ChevronUp className="h-4.5 w-4.5" /> : <ChevronDown className="h-4.5 w-4.5" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden mt-4 pt-4 border-t border-border-custom space-y-4"
          >
            <div className="space-y-2">
              <span className="text-xs font-bold text-text-secondary uppercase">Session Summary</span>
              <p className="text-sm text-text-secondary leading-relaxed bg-surface-secondary/40 p-4 rounded-xl border border-border-custom">
                {item.evaluation_summary || 'No review remarks generated for this session.'}
              </p>
            </div>

            {item.questions && item.questions.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs font-bold text-text-secondary uppercase">Evaluated Questions</span>
                <div className="space-y-1.5">
                  {item.questions.map((q: string, idx: number) => (
                    <div key={idx} className="text-xs text-text-primary flex items-start gap-1.5">
                      <span className="text-accent-primary font-bold">{idx + 1}.</span>
                      <span>{q}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => window.open(`http://localhost:8000/api/interview/${item._id}/report`, '_blank')}
                disabled={item.status !== 'COMPLETED'}
              >
                <Download className="h-4 w-4 mr-1.5" /> Download Report
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

export default function JourneyLogs() {
  const [history, setHistory] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    async function loadHistory() {
      try {
        const list = await interviewService.getHistory();
        setHistory(list);
      } catch (_) {
        setHistory([]);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8 text-left">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">Journey Logs</h1>
        <p className="text-sm text-text-secondary">Explore details, rubrics, and transcripts of historical practice sessions.</p>
      </div>

      {loading ? (
        <div className="min-h-[250px] flex items-center justify-center">
          <div className="h-7 w-7 border-4 border-accent-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : history.length === 0 ? (
        <Card className="p-12 text-center space-y-4 max-w-lg mx-auto">
          <div className="h-12 w-12 bg-surface-secondary border border-border-custom rounded-xl flex items-center justify-center text-text-muted mx-auto">
            <Inbox className="h-6 w-6" />
          </div>
          <div className="space-y-1.5">
            <h3 className="font-semibold text-text-primary text-lg">No sessions completed</h3>
            <p className="text-sm text-text-muted">You have not completed any AI mock practice interviews yet.</p>
          </div>
          <Link href="/practice">
            <Button variant="primary">Start Your First Interview</Button>
          </Link>
        </Card>
      ) : (
        <div className="relative border-l border-border-custom pl-6 ml-4 space-y-8">
          {history.map((item) => (
            <div key={item._id} className="relative">
              {/* Timeline Bullet */}
              <div className="absolute -left-[35px] top-6 h-4.5 w-4.5 rounded-full bg-accent-primary border-4 border-canvas flex items-center justify-center" />
              <JourneyItem item={item} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
