'use client';

import * as React from 'react';
import { useTheme } from 'next-themes';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sun,
  Moon,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle,
  FileText,
  LineChart,
  Brain,
  Upload,
  Sliders,
  Play,
  TrendingUp,
  ChevronDown,
  User,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// Custom Accordion Component for FAQs
function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <div className="border-b border-border-custom last:border-0 py-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left font-medium text-text-primary text-lg py-2 focus:outline-hidden"
      >
        <span>{question}</span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="h-5 w-5 text-text-muted" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <p className="text-text-secondary mt-2 pb-2 leading-relaxed">
              {answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function LandingPage() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState('dashboard');
  const [scrollY, setScrollY] = React.useState(0);

  React.useEffect(() => {
    setMounted(true);
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  const navClass = scrollY > 50
    ? 'fixed top-0 left-0 right-0 z-50 py-3 glass-panel shadow-md'
    : 'fixed top-0 left-0 right-0 z-50 py-5 bg-transparent border-b border-transparent';

  return (
    <div className="min-h-screen relative bg-canvas text-text-primary transition-colors duration-300">
      
      {/* BACKGROUND GRAPHICS */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        {/* Soft floating blur circles */}
        <div className="absolute top-[10%] left-[5%] w-96 h-96 rounded-full bg-accent-primary/10 blur-3xl animate-float" />
        <div className="absolute top-[40%] right-[10%] w-[450px] h-[450px] rounded-full bg-accent-secondary/5 blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-[20%] left-[15%] w-80 h-80 rounded-full bg-accent-primary/5 blur-3xl animate-float" />
      </div>

      {/* HEADER / NAVIGATION */}
      <header className={`${navClass} transition-all duration-300`}>
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="h-9 w-9 rounded-xl bg-accent-primary flex items-center justify-center shadow-lg shadow-accent-primary/20 group-hover:scale-105 transition-transform">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-text-primary">
              Inferexa
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-text-secondary">
            <a href="#features" className="hover:text-text-primary transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-text-primary transition-colors">How It Works</a>
            <a href="#showcase" className="hover:text-text-primary transition-colors">Workspace</a>
            <a href="#testimonials" className="hover:text-text-primary transition-colors">Testimonials</a>
            <a href="#faqs" className="hover:text-text-primary transition-colors">FAQs</a>
          </nav>

          <div className="flex items-center gap-4">
            {mounted && (
              <button
                onClick={toggleTheme}
                className="p-2.5 rounded-xl border border-border-custom hover:bg-surface-secondary text-text-secondary hover:text-text-primary cursor-pointer transition-colors"
                aria-label="Toggle Theme"
              >
                {resolvedTheme === 'dark' ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </button>
            )}

            <Link href="/login">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link href="/login?register=true">
              <Button variant="primary" size="sm">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="relative z-10 min-h-screen pt-32 pb-20 flex items-center max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full">
          
          {/* Left Hero Block */}
          <div className="lg:col-span-6 flex flex-col gap-6 text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-sm font-semibold w-fit">
              <Sparkles className="h-4 w-4" />
              <span>Next-Gen AI Interview Intelligence</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold tracking-tight text-text-primary leading-tight">
              Practice. Improve.<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary to-accent-secondary">
                Get Hired.
              </span>
            </h1>

            <p className="text-lg text-text-secondary leading-relaxed max-w-lg">
              Inferexa is an AI-powered interview intelligence workspace designed for students and professionals. Prepare for technical, behavioral, and system-design tracks with adaptive mock simulations, resume scoring, and predictive feedback.
            </p>

            <div className="flex flex-wrap items-center gap-4 mt-2">
              <Link href="/login">
                <Button variant="primary" size="lg" className="group">
                  <span>Start Practice Session</span>
                  <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <a href="#showcase">
                <Button variant="secondary" size="lg">
                  Watch Demo
                </Button>
              </a>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-border-custom">
              <div className="flex items-center gap-2 text-text-secondary text-sm">
                <ShieldCheck className="h-5 w-5 text-accent-primary shrink-0" />
                <span>IBM Granite AI Evaluator</span>
              </div>
              <div className="flex items-center gap-2 text-text-secondary text-sm">
                <CheckCircle className="h-5 w-5 text-accent-primary shrink-0" />
                <span>STAR Method Grading</span>
              </div>
            </div>
          </div>

          {/* Right Hero Block (Floating Dashboard Showcase) */}
          <div className="lg:col-span-6 flex justify-center relative">
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ repeat: Infinity, duration: 6, ease: 'easeInOut' }}
              className="w-full max-w-[500px] glass-panel rounded-[26px] p-6 shadow-2xl relative border border-border-hover"
            >
              <div className="flex items-center justify-between border-b border-border-custom pb-4 mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-danger" />
                  <div className="h-3 w-3 rounded-full bg-warning" />
                  <div className="h-3 w-3 rounded-full bg-success" />
                </div>
                <div className="text-xs font-mono text-text-muted">inferexa_workspace.session</div>
              </div>

              {/* Chat Simulation Bubble */}
              <div className="space-y-4">
                <div className="p-3.5 rounded-[18px] bg-surface-secondary border border-border-custom text-left">
                  <span className="text-xs text-accent-primary font-bold block mb-1">Granite AI Interviewer</span>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    Explain a scenario where you resolved a complex production latency issue. What was your technical approach?
                  </p>
                </div>

                <div className="p-3.5 rounded-[18px] bg-accent-primary/5 border border-accent-primary/10 text-right ml-8">
                  <span className="text-xs text-accent-secondary font-bold block mb-1">User Candidate</span>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    I optimized our Redis connection pooling configuration and introduced a memcached query layer...
                  </p>
                </div>

                {/* Simulated Skills Radar Panel */}
                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div className="p-3 rounded-xl bg-surface-secondary/55 border border-border-custom text-left">
                    <span className="text-xs text-text-muted block">AI Readiness Score</span>
                    <div className="flex items-baseline gap-1.5 mt-1">
                      <span className="text-2xl font-bold text-success">87%</span>
                      <span className="text-[10px] text-text-muted">Target: 80%</span>
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-surface-secondary/55 border border-border-custom text-left">
                    <span className="text-xs text-text-muted block">Strongest Topic</span>
                    <div className="text-sm font-semibold text-text-primary mt-1">System Design</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

        </div>
      </section>

      {/* WHY INFEREXA SECTION */}
      <section id="features" className="py-24 border-t border-border-custom relative z-10">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold tracking-tight text-text-primary mb-3">
            Crafted for Professional Improvement
          </h2>
          <p className="text-text-secondary text-lg max-w-xl mx-auto mb-16">
            A premium digital suite matching the workflows of fast-paced tech departments.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="flex flex-col items-start text-left gap-4">
              <div className="h-12 w-12 rounded-xl bg-accent-primary/10 border border-accent-primary/20 flex items-center justify-center text-accent-primary">
                <Brain className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary">AI Practice Sessions</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                Experience role-specific technical and behavioral interviews powered by Watsonx and Granite instructions.
              </p>
            </Card>

            <Card className="flex flex-col items-start text-left gap-4">
              <div className="h-12 w-12 rounded-xl bg-accent-secondary/10 border border-accent-secondary/20 flex items-center justify-center text-accent-secondary">
                <FileText className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary">Resume Intelligence</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                Scan your PDF resume to extract key tech competencies, rate compliance indexes, and find missing skill gaps.
              </p>
            </Card>

            <Card className="flex flex-col items-start text-left gap-4">
              <div className="h-12 w-12 rounded-xl bg-success/10 border border-success/20 flex items-center justify-center text-success">
                <LineChart className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary">Insight Analytics</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                Track chronological metrics, monitor score history, evaluate STAR frameworks, and export detailed PDFs.
              </p>
            </Card>

            <Card className="flex flex-col items-start text-left gap-4">
              <div className="h-12 w-12 rounded-xl bg-warning/10 border border-warning/20 flex items-center justify-center text-warning">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary">Adaptive Learning</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                Every subsequent simulation adapts context based on your weak sectors identified in previous runs.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="py-24 bg-surface-primary/30 border-t border-border-custom relative z-10">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold tracking-tight text-text-primary mb-3">
            Streamlined Journey Setup
          </h2>
          <p className="text-text-secondary text-lg max-w-xl mx-auto mb-16">
            Four simple phases to level up your candidate readiness.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
            <div className="flex flex-col items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-surface-secondary border border-border-custom flex items-center justify-center text-accent-primary shadow-sm font-bold text-lg">
                <Upload className="h-6 w-6" />
              </div>
              <h4 className="font-semibold text-text-primary text-lg">1. Upload Resume</h4>
              <p className="text-sm text-text-secondary max-w-xs leading-relaxed">
                Upload your latest PDF profile to instantly extract standard skills and projects.
              </p>
            </div>

            <div className="flex flex-col items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-surface-secondary border border-border-custom flex items-center justify-center text-accent-primary shadow-sm font-bold text-lg">
                <Sliders className="h-6 w-6" />
              </div>
              <h4 className="font-semibold text-text-primary text-lg">2. Setup Interview</h4>
              <p className="text-sm text-text-secondary max-w-xs leading-relaxed">
                Choose target role, difficulty tracks, question lengths, and language focus.
              </p>
            </div>

            <div className="flex flex-col items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-surface-secondary border border-border-custom flex items-center justify-center text-accent-primary shadow-sm font-bold text-lg">
                <Play className="h-6 w-6" />
              </div>
              <h4 className="font-semibold text-text-primary text-lg">3. Simulate with AI</h4>
              <p className="text-sm text-text-secondary max-w-xs leading-relaxed">
                Respond to conversational, responsive questions streamed in real-time.
              </p>
            </div>

            <div className="flex flex-col items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-surface-secondary border border-border-custom flex items-center justify-center text-accent-primary shadow-sm font-bold text-lg">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h4 className="font-semibold text-text-primary text-lg">4. Get Inspected</h4>
              <p className="text-sm text-text-secondary max-w-xs leading-relaxed">
                Analyze score reports, feedback notes, and recommendations instantly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* PRODUCT SHOWCASE */}
      <section id="showcase" className="py-24 border-t border-border-custom relative z-10">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold tracking-tight text-text-primary mb-3">
            Unified Digital Workspace
          </h2>
          <p className="text-text-secondary text-lg max-w-xl mx-auto mb-12">
            Alternate between tools dynamically in one premium client application.
          </p>

          <div className="flex items-center justify-center gap-2 mb-8 bg-surface-secondary/70 p-1.5 rounded-2xl border border-border-custom w-fit mx-auto">
            {['dashboard', 'practice', 'resume', 'performance'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-2.5 text-sm font-semibold rounded-xl capitalize transition-all cursor-pointer ${
                  activeTab === tab
                    ? 'bg-accent-primary text-white shadow-sm'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Browser Container Mockup */}
          <div className="w-full max-w-5xl mx-auto rounded-3xl border border-border-hover glass-panel p-6 shadow-2xl min-h-[400px] flex items-center justify-center">
            {activeTab === 'dashboard' && (
              <div className="w-full text-left space-y-6">
                <div className="flex justify-between items-center pb-4 border-b border-border-custom">
                  <div>
                    <h4 className="text-xl font-bold text-text-primary">Dashboard Overview</h4>
                    <p className="text-sm text-text-secondary">Welcome back, candidate</p>
                  </div>
                  <span className="text-xs font-semibold px-3 py-1 bg-success/15 text-success rounded-full">Active Streak: 5 Days</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 border border-border-custom bg-surface-secondary rounded-2xl">
                    <span className="text-xs text-text-muted block">AI Interview Rating</span>
                    <span className="text-3xl font-bold text-text-primary block mt-1">8.5/10</span>
                  </div>
                  <div className="p-4 border border-border-custom bg-surface-secondary rounded-2xl">
                    <span className="text-xs text-text-muted block">Ready Index</span>
                    <span className="text-3xl font-bold text-accent-primary block mt-1">A+ Class</span>
                  </div>
                  <div className="p-4 border border-border-custom bg-surface-secondary rounded-2xl">
                    <span className="text-xs text-text-muted block">Practiced Sessions</span>
                    <span className="text-3xl font-bold text-accent-secondary block mt-1">12 Complete</span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'practice' && (
              <div className="w-full text-left space-y-6">
                <h4 className="text-xl font-bold text-text-primary">Interactive Studio Simulator</h4>
                <div className="p-5 border border-border-custom bg-surface-secondary rounded-2xl flex items-center justify-between gap-4">
                  <div>
                    <span className="text-xs font-mono text-accent-primary">Granite Evaluator</span>
                    <p className="text-base text-text-primary font-medium mt-1">
                      "Could you describe how you configure horizontal auto-scaling inside Kubernetes?"
                    </p>
                  </div>
                  <div className="h-4 w-4 bg-accent-primary rounded-full animate-ping" />
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-3 py-1.5 text-xs bg-surface-elevated border border-border-custom text-text-secondary rounded-lg">Target: DevOps</span>
                  <span className="px-3 py-1.5 text-xs bg-surface-elevated border border-border-custom text-text-secondary rounded-lg">Intermediate</span>
                </div>
              </div>
            )}

            {activeTab === 'resume' && (
              <div className="w-full text-left space-y-6">
                <h4 className="text-xl font-bold text-text-primary">Resume Parsing & Compliance</h4>
                <div className="p-6 border border-dashed border-border-hover bg-surface-secondary/45 rounded-2xl text-center space-y-2">
                  <Upload className="h-8 w-8 text-accent-primary mx-auto" />
                  <p className="text-sm font-semibold text-text-primary">drag_and_drop_profile.pdf</p>
                  <p className="text-xs text-text-muted">Extracted 14 tech assets / calculated score: 92% match</p>
                </div>
              </div>
            )}

            {activeTab === 'performance' && (
              <div className="w-full text-left space-y-6">
                <h4 className="text-xl font-bold text-text-primary">Analytics Progress Timeline</h4>
                <div className="h-48 border border-border-custom bg-surface-secondary rounded-2xl flex items-end justify-between p-4">
                  {[40, 55, 45, 60, 75, 70, 85, 90].map((height, idx) => (
                    <div key={idx} className="flex flex-col items-center gap-2 w-[8%]">
                      <div className="w-full bg-accent-primary rounded-t-md" style={{ height: `${height}%` }} />
                      <span className="text-[10px] text-text-muted">Run {idx + 1}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section id="testimonials" className="py-24 bg-surface-primary/30 border-t border-border-custom relative z-10">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold tracking-tight text-text-primary mb-3">
            Endorsed by Professionals
          </h2>
          <p className="text-text-secondary text-lg max-w-xl mx-auto mb-16">
            Hear from candidates who successfully leveraged Inferexa workspace.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="flex flex-col text-left gap-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-accent-primary/20 flex items-center justify-center text-accent-primary">
                  <User className="h-5 w-5" />
                </div>
                <div>
                  <span className="font-semibold text-text-primary block">Supriya B.</span>
                  <span className="text-xs text-text-muted">Software Engineer Graduate</span>
                </div>
              </div>
              <p className="text-sm text-text-secondary leading-relaxed">
                "The structured breakdown and chronological progress tracker gave me complete confidence. Streamlining my responses into the STAR framework helped me crack my top-tier SaaS role."
              </p>
            </Card>

            <Card className="flex flex-col text-left gap-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-accent-secondary/20 flex items-center justify-center text-accent-secondary">
                  <User className="h-5 w-5" />
                </div>
                <div>
                  <span className="font-semibold text-text-primary block">Alex M.</span>
                  <span className="text-xs text-text-muted">Backend Developer Candidate</span>
                </div>
              </div>
              <p className="text-sm text-text-secondary leading-relaxed">
                "Comparing resume analytics dynamically and getting instant missing-skill notifications pointed out my exact blind spots before the live loop. Highly premium experience."
              </p>
            </Card>

            <Card className="flex flex-col text-left gap-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-success/20 flex items-center justify-center text-success">
                  <User className="h-5 w-5" />
                </div>
                <div>
                  <span className="font-semibold text-text-primary block">Jane R.</span>
                  <span className="text-xs text-text-muted">Product Manager Lead</span>
                </div>
              </div>
              <p className="text-sm text-text-secondary leading-relaxed">
                "The Granite AI model simulation feels like speaking to a real, experienced interviewer. The timing countdown and immediate scorecard reports are incredibly detailed."
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQS */}
      <section id="faqs" className="py-24 border-t border-border-custom relative z-10">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center text-text-primary mb-12">
            Frequently Asked Questions
          </h2>

          <div className="border border-border-custom bg-surface-primary rounded-[22px] px-6 py-4">
            <FAQItem
              question="What AI engine does Inferexa use?"
              answer="Inferexa uses the high-performance IBM Granite-3-8b-instruct model, connected via IBM Cloud watsonx AI service layers to generate accurate role-specific interview queries."
            />
            <FAQItem
              question="Can I practice both technical coding and behavioral tracks?"
              answer="Yes! Practice Studio provides options for Technical, System Design, Behavioral (using the STAR evaluation framework), HR, or Mixed session configurations."
            />
            <FAQItem
              question="Is my resume parsed securely?"
              answer="Yes, all document uploads are scanned securely and processed directly. Database storage defaults locally unless your IBM Cloud Object Storage is customized."
            />
            <FAQItem
              question="How are my mock answers rated?"
              answer="Your transcript responses are checked against standard grading templates and technical vector stores. The system analyzes clarity, correctness, and structure."
            />
          </div>
        </div>
      </section>

      {/* FINAL CALL TO ACTION */}
      <section className="py-24 border-t border-border-custom relative z-10 text-center bg-gradient-to-b from-transparent to-accent-primary/5">
        <div className="max-w-4xl mx-auto px-6 space-y-6">
          <h2 className="text-4xl lg:text-5xl font-bold text-text-primary tracking-tight">
            Ready to transform your interview preparation?
          </h2>
          <p className="text-lg text-text-secondary max-w-xl mx-auto">
            Create your account today and experience our premium simulated interview intelligence.
          </p>
          <div className="flex justify-center items-center gap-4 pt-4">
            <Link href="/login?register=true">
              <Button variant="primary" size="lg">
                Get Started
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="secondary" size="lg">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border-custom bg-surface-primary py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col items-center md:items-start gap-2">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-lg bg-accent-primary flex items-center justify-center text-white text-xs">
                <Sparkles className="h-3.5 w-3.5" />
              </div>
              <span className="text-lg font-bold tracking-tight text-text-primary">
                Inferexa
              </span>
            </div>
            <p className="text-xs text-text-muted">Practice. Improve. Get Hired.</p>
          </div>

          <div className="flex items-center gap-6 text-sm text-text-secondary">
            <a href="#features" className="hover:text-text-primary transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-text-primary transition-colors">About</a>
            <a href="#" className="hover:text-text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-text-primary transition-colors">Terms of Service</a>
          </div>

          <div className="flex items-center gap-4 text-text-muted">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-text-primary transition-colors" aria-label="GitHub">
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.577.688.479C19.138 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z"/></svg>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="hover:text-text-primary transition-colors" aria-label="LinkedIn">
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
