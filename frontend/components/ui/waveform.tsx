'use client';

import * as React from 'react';
import { motion } from 'framer-motion';

export function Waveform({ active = true }: { active?: boolean }) {
  const bars = Array.from({ length: 15 }, (_, i) => i);

  return (
    <div className="flex items-center gap-1.5 h-12 px-4 py-2 bg-surface-secondary border border-border-custom rounded-full">
      {bars.map((bar) => (
        <motion.div
          key={bar}
          className="w-1 rounded-full bg-accent-primary"
          initial={{ height: 4 }}
          animate={
            active
              ? {
                  height: [6, 28, 10, 36, 14, 6][bar % 6],
                }
              : { height: 4 }
          }
          transition={{
            repeat: Infinity,
            repeatType: 'reverse',
            duration: 1 + (bar % 3) * 0.25,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}
