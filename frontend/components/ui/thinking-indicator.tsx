'use client';

import * as React from 'react';
import { motion } from 'framer-motion';

export function ThinkingIndicator({ text = 'AI is thinking' }: { text?: string }) {
  return (
    <div className="flex items-center gap-3 px-5 py-3.5 bg-surface-secondary border border-border-custom rounded-[18px] max-w-xs shadow-sm">
      <div className="flex items-center gap-1.5">
        {[0, 1, 2].map((dot) => (
          <motion.div
            key={dot}
            className="h-2 w-2 rounded-full bg-accent-primary"
            animate={{
              y: [0, -6, 0],
            }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: dot * 0.15,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
      <span className="text-sm font-medium text-text-secondary select-none">
        {text}...
      </span>
    </div>
  );
}

export function StreamingText({ text, speed = 25 }: { text: string; speed?: number }) {
  const [displayedText, setDisplayedText] = React.useState('');

  React.useEffect(() => {
    let index = 0;
    setDisplayedText('');
    
    const interval = setInterval(() => {
      if (index < text.length) {
        setDisplayedText((prev) => prev + text.charAt(index));
        index++;
      } else {
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <span className="inline-block relative">
      {displayedText}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ repeat: Infinity, duration: 0.6 }}
        className="inline-block w-1.5 h-4 bg-accent-primary ml-1 align-middle"
      />
    </span>
  );
}
