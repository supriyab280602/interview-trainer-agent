'use client';

import * as React from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, Check } from 'lucide-react';
import { authService } from '@/services/auth';
import { useAuthStore } from '@/store';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

function AuthPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isRegisterParam = searchParams.get('register') === 'true';

  const [isRegister, setIsRegister] = React.useState(isRegisterParam);
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [fullName, setFullName] = React.useState('');
  const [role, setRole] = React.useState('');
  
  // Validation and states
  const [loading, setLoading] = React.useState(false);
  const [success, setSuccess] = React.useState(false);
  const [error, setError] = React.useState('');

  React.useEffect(() => {
    setIsRegister(searchParams.get('register') === 'true');
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password || (isRegister && (!fullName || !role))) {
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);

    try {
      if (isRegister) {
        await authService.signup({
          full_name: fullName,
          email,
          password,
          confirm_password: password,
        });

        // Auto update profile after registration to link the role
        const loginRes = await authService.login({ email, password });
        useAuthStore.getState().setAuth(loginRes.user, loginRes.session_id);
        
        await authService.updateProfile({
          profile_name: 'default',
          experience_level: '1-3 Years',
          target_role: role,
        });
      } else {
        const res = await authService.login({ email, password });
        useAuthStore.getState().setAuth(res.user, res.session_id);
      }

      setSuccess(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-canvas overflow-hidden">
      
      {/* LEFT PANEL: Branding & Visuals */}
      <div className="hidden lg:flex lg:col-span-6 relative flex-col justify-between p-12 bg-surface-primary border-r border-border-custom overflow-hidden">
        {/* Animated Background Gradients */}
        <div className="absolute inset-0 pointer-events-none z-0">
          <div className="absolute top-[20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-accent-primary/10 blur-3xl animate-float" />
          <div className="absolute bottom-[10%] right-[-10%] w-[400px] h-[400px] rounded-full bg-accent-secondary/5 blur-3xl animate-pulse-slow" />
        </div>

        <div className="relative z-10 flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-accent-primary flex items-center justify-center shadow-lg shadow-accent-primary/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-text-primary">
            Inferexa
          </span>
        </div>

        <div className="relative z-10 max-w-md my-auto space-y-6 text-left">
          <h2 className="text-4xl font-bold tracking-tight text-text-primary leading-tight">
            Your AI-powered interview intelligence workspace.
          </h2>
          <p className="text-base text-text-secondary leading-relaxed">
            Designed to help you build confidence, identify performance indicators, map resume discrepancies, and achieve career success.
          </p>
        </div>

        <div className="relative z-10 flex items-center justify-between text-xs text-text-muted">
          <span>Inferexa Platform v1.0</span>
          <span>© 2026 Inferexa Inc.</span>
        </div>
      </div>

      {/* RIGHT PANEL: Form card */}
      <div className="lg:col-span-6 flex items-center justify-center p-6 relative">
        <div className="absolute inset-0 pointer-events-none lg:hidden overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-80 h-80 rounded-full bg-accent-primary/5 blur-3xl" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-[460px] glass-panel rounded-[26px] p-8 shadow-2xl relative z-10 border border-border-hover"
        >
          <div className="space-y-2 text-center lg:text-left mb-8">
            <h1 className="text-3xl font-bold text-text-primary">
              {isRegister ? 'Create Account' : 'Welcome Back'}
            </h1>
            <p className="text-sm text-text-secondary">
              {isRegister ? 'Begin your interview intelligence journey.' : 'Continue your interview journey.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5 text-left">
            <AnimatePresence mode="popLayout">
              {isRegister && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-5"
                >
                  <Input
                    label="Full Name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    onClear={() => setFullName('')}
                    required
                  />
                  <Input
                    label="Target Professional Role"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    onClear={() => setRole('')}
                    placeholder="e.g. Software Engineer, Product Manager"
                    required
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <Input
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onClear={() => setEmail('')}
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {error && (
              <p className="text-sm text-danger font-medium mt-1">{error}</p>
            )}

            {!isRegister && (
              <div className="flex items-center justify-between text-sm py-1">
                <label className="flex items-center gap-2 text-text-secondary cursor-pointer select-none">
                  <input
                    type="checkbox"
                    className="rounded-md border-border-custom bg-surface-secondary text-accent-primary focus:ring-accent-primary"
                  />
                  <span>Remember me</span>
                </label>
                <a href="#" className="text-accent-primary hover:underline">
                  Forgot Password?
                </a>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-2"
              isLoading={loading}
              isSuccess={success}
            >
              {success ? (
                <span className="flex items-center gap-2 justify-center">
                  <Check className="h-5 w-5" /> Authenticated
                </span>
              ) : isRegister ? (
                'Create Workspace'
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          {/* Social Divider */}
          <div className="relative flex items-center justify-center my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border-custom"></div>
            </div>
            <span className="relative px-3 bg-surface-primary/10 backdrop-blur-md text-xs text-text-muted uppercase">
              Or continue with
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button variant="secondary" size="sm" onClick={() => {}} className="py-2.5">
              <svg className="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="currentColor"><path d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114-3.41 0-6.19-2.78-6.19-6.19 0-3.41 2.78-6.19 6.19-6.19 1.547 0 2.946.568 4.027 1.49l3.19-3.19C19.23 2.1 15.93.9 12.24.9 6.01.9 1 5.91 1 12.14s5.01 11.24 11.24 11.24c5.89 0 10.8-4.114 10.8-11.24 0-.61-.06-1.18-.18-1.74l-10.62-.115z"/></svg> Google
            </Button>
            <Button variant="secondary" size="sm" onClick={() => {}} className="py-2.5">
              <svg className="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="currentColor"><path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.577.688.479C19.138 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z"/></svg> GitHub
            </Button>
          </div>

          {/* Switch flow */}
          <div className="mt-8 text-center text-sm text-text-secondary">
            {isRegister ? (
              <span>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsRegister(false)}
                  className="text-accent-primary font-semibold hover:underline bg-transparent border-0 cursor-pointer"
                >
                  Sign In
                </button>
              </span>
            ) : (
              <span>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsRegister(true)}
                  className="text-accent-primary font-semibold hover:underline bg-transparent border-0 cursor-pointer"
                >
                  Create Account
                </button>
              </span>
            )}
          </div>

        </motion.div>
      </div>

    </div>
  );
}

export default function AuthPage() {
  return (
    <React.Suspense fallback={<div className="min-h-screen bg-canvas flex items-center justify-center text-text-muted">Loading Auth Workspace...</div>}>
      <AuthPageInner />
    </React.Suspense>
  );
}
