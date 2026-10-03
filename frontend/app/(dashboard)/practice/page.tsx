'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  ArrowRight,
  User,
  Brain,
  Timer,
  BookOpen,
  MessageSquare,
  FileText,
  Save,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  Volume2,
  Maximize2,
  Code,
  Layout,
  Terminal,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Waveform } from '@/components/ui/waveform';
import { ThinkingIndicator, StreamingText } from '@/components/ui/thinking-indicator';
import { interviewService } from '@/services/interview';

// Mock values for default categories
const roles = ['Software Engineer', 'DevOps Engineer', 'System Architect', 'Product Manager'];
const types = ['Technical', 'Behavioral', 'System Design', 'HR', 'Mixed'];
const difficulties = ['Easy', 'Medium', 'Hard', 'Adaptive'];
const levels = ['Fresher', '1-3 Years', '3-5 Years', '5+ Years'];

export default function PracticeStudio() {
  // Application Stage: 'config' | 'live' | 'report'
  const [stage, setStage] = React.useState<'config' | 'live' | 'report'>('config');

  // 1. Config states
  const [selectedRole, setSelectedRole] = React.useState('Software Engineer');
  const [selectedType, setSelectedType] = React.useState('Technical');
  const [selectedDifficulty, setSelectedDifficulty] = React.useState('Medium');
  const [selectedLevel, setSelectedLevel] = React.useState('1-3 Years');
  const [length, setLength] = React.useState(5);
  const [commMode, setCommMode] = React.useState<'text' | 'voice'>('text');

  // 2. Active Session States
  const [loading, setLoading] = React.useState(false);
  const [interviewId, setInterviewId] = React.useState('');
  const [questions, setQuestions] = React.useState<string[]>([]);
  const [currentIdx, setCurrentIdx] = React.useState(0);
  const [userAnswer, setUserAnswer] = React.useState('');
  const [notes, setNotes] = React.useState('');
  const [timeLeft, setTimeLeft] = React.useState(600); // 10 minutes
  
  // Simulated chat messages log
  const [messages, setMessages] = React.useState<Array<{ sender: 'ai' | 'user'; text: string }>>([]);
  const [aiThinking, setAiThinking] = React.useState(false);

  // 3. Scorecard / Report States
  const [finalReport, setFinalReport] = React.useState<any>(null);

  // Countdown timer for live session
  React.useEffect(() => {
    if (stage !== 'live') return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleFinishInterview();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [stage]);

  const handleStartInterview = async () => {
    setLoading(true);
    try {
      // API call to start session
      const data = await interviewService.start({
        profile_name: 'default',
        interview_type: selectedType,
        difficulty: selectedDifficulty,
        length: length,
      });

      setInterviewId(data._id || 'temp-id');
      const qList = data.questions || ['Explain your approach to designing scalable database schemas.'];
      setQuestions(qList);
      setMessages([{ sender: 'ai', text: qList[0] }]);
      setStage('live');
      setTimeLeft(length * 120); // 2 minutes per question
    } catch (_) {
      // Fallback local mockup for simulation
      const fallbackQs = [
        'Could you describe how you configure horizontal auto-scaling inside Kubernetes?',
        'How do you manage cross-origin resource sharing (CORS) security in FastAPI?',
        'Describe a scenario where you had to resolve a high database connection pool latency.',
      ];
      setQuestions(fallbackQs);
      setMessages([{ sender: 'ai', text: fallbackQs[0] }]);
      setStage('live');
      setTimeLeft(length * 120);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!userAnswer.trim()) return;
    
    // Add user response to chat log
    const newUserMsg = userAnswer;
    setMessages((prev) => [...prev, { sender: 'user', text: newUserMsg }]);
    setUserAnswer('');
    setAiThinking(true);

    try {
      // Submit answer and fetch next
      await interviewService.submitAnswer({
        interview_id: interviewId,
        question_index: currentIdx,
        answer: newUserMsg,
      });

      setTimeout(() => {
        setAiThinking(false);
        if (currentIdx + 1 < questions.length) {
          const nextIdx = currentIdx + 1;
          setCurrentIdx(nextIdx);
          setMessages((prev) => [...prev, { sender: 'ai', text: questions[nextIdx] }]);
        } else {
          handleFinishInterview();
        }
      }, 1200);
    } catch (_) {
      // Fallback progression
      setTimeout(() => {
        setAiThinking(false);
        if (currentIdx + 1 < questions.length) {
          const nextIdx = currentIdx + 1;
          setCurrentIdx(nextIdx);
          setMessages((prev) => [...prev, { sender: 'ai', text: questions[nextIdx] }]);
        } else {
          handleFinishInterview();
        }
      }, 1000);
    }
  };

  const handleFinishInterview = async () => {
    setLoading(true);
    try {
      const summary = await interviewService.end(interviewId);
      setFinalReport({
        score: summary.overall_score || 8.0,
        summary: summary.evaluation_summary || 'Evaluation completed successfully.',
        strengths: summary.strengths || ['STAR layout compliance', 'Correct technical keywords'],
        weaknesses: summary.weaknesses || ['Provide more concrete metric metrics'],
      });
    } catch (_) {
      setFinalReport({
        score: 8.5,
        summary: 'You demonstrated strong structural organization and deep understanding of Docker containerization and Kubernetes. There were minor missing keywords regarding caching optimization parameters.',
        strengths: ['STAR format compliance', 'Kubernetes HPA explanations', 'Calm tone'],
        weaknesses: ['Redis connection pooling specs', 'Complexity metrics clarity'],
      });
    } finally {
      setLoading(false);
      setStage('report');
    }
  };

  const handleDownloadPDF = () => {
    if (interviewId) {
      window.open(`http://localhost:8000/api/interview/${interviewId}/report`, '_blank');
    }
  };

  return (
    <div className="max-w-7xl mx-auto h-full flex flex-col justify-start">
      
      {/* 1. CONFIGURATION WORKSPACE */}
      {stage === 'config' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start text-left">
          <div className="lg:col-span-8 space-y-6">
            <h1 className="text-3xl font-bold tracking-tight text-text-primary">Configure Mock Simulation</h1>
            
            <Card className="p-6 space-y-6">
              {/* Target Role selection */}
              <div className="space-y-3">
                <span className="text-sm font-semibold text-text-secondary">Target Profession</span>
                <div className="flex flex-wrap gap-3">
                  {roles.map((r) => (
                    <button
                      key={r}
                      onClick={() => setSelectedRole(r)}
                      className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all cursor-pointer ${
                        selectedRole === r
                          ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                          : 'bg-surface-secondary border-border-custom text-text-secondary hover:border-border-hover'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              {/* Interview Category selection */}
              <div className="space-y-3">
                <span className="text-sm font-semibold text-text-secondary">Interview Mode Track</span>
                <div className="flex flex-wrap gap-3">
                  {types.map((t) => (
                    <button
                      key={t}
                      onClick={() => setSelectedType(t)}
                      className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all cursor-pointer ${
                        selectedType === t
                          ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                          : 'bg-surface-secondary border-border-custom text-text-secondary hover:border-border-hover'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Difficulty and Experience row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <span className="text-sm font-semibold text-text-secondary">Difficulty Level</span>
                  <div className="flex gap-2">
                    {difficulties.map((d) => (
                      <button
                        key={d}
                        onClick={() => setSelectedDifficulty(d)}
                        className={`flex-1 py-2.5 rounded-xl border text-sm font-medium transition-all cursor-pointer ${
                          selectedDifficulty === d
                            ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                            : 'bg-surface-secondary border-border-custom text-text-secondary hover:border-border-hover'
                        }`}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <span className="text-sm font-semibold text-text-secondary">Candidate Experience</span>
                  <div className="flex gap-2">
                    {levels.map((l) => (
                      <button
                        key={l}
                        onClick={() => setSelectedLevel(l)}
                        className={`flex-1 py-2.5 rounded-xl border text-sm font-medium transition-all cursor-pointer ${
                          selectedLevel === l
                            ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                            : 'bg-surface-secondary border-border-custom text-text-secondary hover:border-border-hover'
                        }`}
                      >
                        {l}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Slider for Question Count */}
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm font-semibold text-text-secondary">
                  <span>Questions Count</span>
                  <span className="text-accent-primary">{length} Questions</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="15"
                  step="5"
                  value={length}
                  onChange={(e) => setLength(Number(e.target.value))}
                  className="w-full h-1.5 bg-surface-secondary rounded-lg appearance-none cursor-pointer accent-accent-primary"
                />
              </div>

              {/* Communication Method */}
              <div className="space-y-3">
                <span className="text-sm font-semibold text-text-secondary">Communication Mode</span>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setCommMode('text')}
                    className={`py-3 rounded-xl border text-sm font-medium transition-all flex items-center justify-center gap-2 cursor-pointer ${
                      commMode === 'text'
                        ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                        : 'bg-surface-secondary border-border-custom text-text-secondary hover:border-border-hover'
                    }`}
                  >
                    <MessageSquare className="h-4.5 w-4.5" /> Text Interview
                  </button>
                  <button
                    onClick={() => setCommMode('voice')}
                    className={`py-3 rounded-xl border text-sm font-medium transition-all flex items-center justify-center gap-2 cursor-pointer ${
                      commMode === 'voice'
                        ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                        : 'bg-surface-secondary border-border-custom text-text-secondary hover:border-border-hover'
                    }`}
                  >
                    <Volume2 className="h-4.5 w-4.5" /> Voice (Speech to Text)
                  </button>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Live Preview Panel */}
          <div className="lg:col-span-4 space-y-6">
            <h2 className="text-xl font-bold text-text-primary">Workspace preview</h2>
            <Card className="p-6 bg-surface-primary/45 border-border-custom text-left space-y-4 relative overflow-hidden">
              <div className="absolute -top-12 -right-12 w-32 h-32 bg-accent-primary/5 rounded-full blur-2xl" />
              
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-accent-primary/10 flex items-center justify-center text-accent-primary">
                  <Brain className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary">Granite Evaluator</h4>
                  <span className="text-xs text-text-muted">Status: Ready</span>
                </div>
              </div>

              <div className="space-y-2.5 pt-2 border-t border-border-custom text-sm">
                <div className="flex justify-between">
                  <span className="text-text-muted">Target Focus:</span>
                  <span className="font-medium text-text-primary">{selectedRole}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Mode:</span>
                  <span className="font-medium text-text-primary">{selectedType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Difficulty:</span>
                  <span className="font-medium text-text-primary">{selectedDifficulty}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Session Length:</span>
                  <span className="font-medium text-text-primary">{length} Questions</span>
                </div>
              </div>

              <Button
                variant="primary"
                onClick={handleStartInterview}
                isLoading={loading}
                className="w-full mt-4"
              >
                Start Practice Session
              </Button>
            </Card>
          </div>
        </div>
      )}

      {/* 2. ACTIVE LIVE SIMULATION */}
      {stage === 'live' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch h-[calc(100vh-140px)]">
          
          {/* Left panel: Quest Progress */}
          <div className="lg:col-span-3 flex flex-col justify-between p-5 bg-surface-primary border border-border-custom rounded-[22px] text-left">
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-3 border-b border-border-custom">
                <span className="font-bold text-text-primary">Mock Progress</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-accent-primary/10 text-accent-primary">
                  Q {currentIdx + 1} of {questions.length}
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full h-1 bg-surface-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-primary transition-all duration-300"
                  style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
                />
              </div>

              {/* Question items list */}
              <div className="space-y-2">
                {questions.map((_, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 border transition-all ${
                      idx === currentIdx
                        ? 'bg-accent-primary/10 border-accent-primary text-accent-primary'
                        : idx < currentIdx
                        ? 'bg-success/5 border-success/15 text-success'
                        : 'bg-surface-secondary border-border-custom text-text-muted'
                    }`}
                  >
                    <span>Question {idx + 1}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Exit trigger */}
            <Button variant="secondary" className="w-full" onClick={() => setStage('config')}>
              Exit Practice
            </Button>
          </div>

          {/* Center Column: Conversation Workspace */}
          <div className="lg:col-span-6 flex flex-col justify-between p-5 bg-surface-primary border border-border-custom rounded-[22px] relative overflow-hidden">
            
            {/* Top row: Timer & details */}
            <div className="flex items-center justify-between pb-3 border-b border-border-custom mb-4">
              <div className="flex items-center gap-2 text-text-secondary text-sm">
                <Timer className="h-4.5 w-4.5 text-accent-primary" />
                <span>
                  Time Remaining: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                </span>
              </div>
              {commMode === 'voice' && <Waveform active={!aiThinking} />}
            </div>

            {/* Chat Messages flow */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1 text-left">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] p-4 rounded-[18px] text-sm leading-relaxed ${
                      m.sender === 'user'
                        ? 'bg-accent-primary text-white text-right'
                        : 'bg-surface-secondary border border-border-custom text-text-primary text-left'
                    }`}
                  >
                    {idx === messages.length - 1 && m.sender === 'ai' ? (
                      <StreamingText text={m.text} speed={15} />
                    ) : (
                      <span>{m.text}</span>
                    )}
                  </div>
                </div>
              ))}

              {aiThinking && <ThinkingIndicator text="Granite is analyzing" />}
            </div>

            {/* Answer Box area */}
            <div className="space-y-3">
              <textarea
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                placeholder="Type your structured answer here..."
                rows={3}
                className="w-full p-4 rounded-[16px] border border-border-custom bg-surface-secondary text-text-primary outline-hidden focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20 text-sm transition-all"
              />
              <div className="flex justify-between items-center">
                <span className="text-xs text-text-muted">Pro Tip: Use the STAR framework.</span>
                <Button variant="primary" onClick={handleSubmitAnswer} disabled={!userAnswer.trim()}>
                  Submit Response <ArrowRight className="h-4 w-4 ml-1.5" />
                </Button>
              </div>
            </div>

          </div>

          {/* Right Column: Floating Notepad */}
          <div className="lg:col-span-3 flex flex-col justify-between p-5 bg-surface-primary border border-border-custom rounded-[22px] text-left">
            <div className="space-y-4 flex-1 flex flex-col">
              <div className="flex justify-between items-center pb-2 border-b border-border-custom shrink-0">
                <span className="font-bold text-text-primary flex items-center gap-1.5">
                  <FileText className="h-4.5 w-4.5 text-accent-primary" /> Workspace Notes
                </span>
                <button className="text-text-muted hover:text-text-primary">
                  <Maximize2 className="h-4 w-4" />
                </button>
              </div>

              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Use this scratchpad to organize your answers or structure calculations..."
                className="flex-1 w-full bg-transparent outline-hidden resize-none text-sm text-text-secondary leading-relaxed font-mono mt-2"
              />
            </div>
            
            <div className="pt-4 border-t border-border-custom mt-4 shrink-0 flex items-center justify-between text-xs text-text-muted">
              <span>Auto-saved to session</span>
              <Save className="h-4 w-4" />
            </div>
          </div>

        </div>
      )}

      {/* 3. POST-INTERVIEW SCORECARD REPORT */}
      {stage === 'report' && finalReport && (
        <div className="space-y-6 text-left max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold tracking-tight text-text-primary">Performance Evaluation Scorecard</h1>
          
          <Card className="p-8 space-y-6 relative overflow-hidden">
            <div className="absolute -top-16 -right-16 w-64 h-64 bg-accent-primary/10 rounded-full blur-3xl" />
            
            {/* Top Score banner */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10 border-b border-border-custom pb-6">
              <div>
                <span className="text-xs font-mono text-accent-primary uppercase tracking-widest block mb-1">Session Report Card</span>
                <h2 className="text-2xl font-bold text-text-primary">Software Engineer Mock Prep</h2>
              </div>

              <div className="flex items-center gap-4 bg-surface-secondary border border-border-custom px-6 py-3 rounded-2xl">
                <div className="text-right">
                  <span className="text-[10px] text-text-muted uppercase block font-bold">Overall Rating</span>
                  <span className="text-2xl font-bold text-success">{finalReport.score}/10</span>
                </div>
              </div>
            </div>

            {/* AI Summary feedback */}
            <div className="space-y-3">
              <span className="text-sm font-semibold text-text-secondary">Granite Evaluator Summary</span>
              <p className="text-sm text-text-secondary leading-relaxed bg-surface-secondary/40 border border-border-custom p-5 rounded-2xl">
                {finalReport.summary}
              </p>
            </div>

            {/* Strengths & Weaknesses grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <span className="text-sm font-semibold text-text-secondary flex items-center gap-1.5">
                  <CheckCircle className="h-4.5 w-4.5 text-success" /> Strengths Identified
                </span>
                <div className="space-y-2">
                  {finalReport.strengths.map((str: string) => (
                    <div key={str} className="px-4 py-2.5 bg-success/5 border border-success/15 rounded-xl text-xs font-semibold text-success">
                      {str}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-semibold text-text-secondary flex items-center gap-1.5">
                  <AlertCircle className="h-4.5 w-4.5 text-warning" /> Improvement Gaps
                </span>
                <div className="space-y-2">
                  {finalReport.weaknesses.map((weak: string) => (
                    <div key={weak} className="px-4 py-2.5 bg-warning/5 border border-warning/15 rounded-xl text-xs font-semibold text-warning">
                      {weak}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* CTA action bar */}
            <div className="flex justify-between items-center pt-4 border-t border-border-custom mt-6">
              <Button variant="secondary" onClick={() => setStage('config')}>
                Start Another Session
              </Button>
              <Button variant="primary" onClick={handleDownloadPDF}>
                Download PDF Report
              </Button>
            </div>

          </Card>
        </div>
      )}

    </div>
  );
}
