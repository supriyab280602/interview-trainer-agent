'use client';

import * as React from 'react';
import { motion } from 'framer-motion';

interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onDrag' | 'onDragStart' | 'onDragEnd' | 'onDragOver' | 'onDragEnter' | 'onDragLeave' | 'onDragExit' | 'onAnimationStart'> {
  hoverEffect?: boolean;
  glass?: boolean;
}

export function Card({
  children,
  hoverEffect = true,
  glass = false,
  className = '',
  ...props
}: CardProps) {
  const baseClasses = `rounded-[22px] border p-6 transition-all duration-300 ${
    glass
      ? 'glass-panel'
      : 'bg-surface-primary border-border-custom shadow-sm'
  }`;

  if (!hoverEffect) {
    return (
      <div className={`${baseClasses} ${className}`} {...props}>
        {children}
      </div>
    );
  }

  return (
    <motion.div
      whileHover={{
        y: -6,
        scale: 1.015,
        boxShadow: 'var(--shadow-md)',
        borderColor: 'var(--border-hover)',
        backgroundColor: 'var(--surface-secondary)',
      }}
      transition={{ type: 'spring', stiffness: 350, damping: 25 }}
      className={`${baseClasses} ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function CardHeader({ children, className = '', ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`flex flex-col gap-1.5 mb-4 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '', ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={`text-xl font-semibold text-text-primary tracking-tight ${className}`} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ children, className = '', ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={`text-sm text-text-muted ${className}`} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ children, className = '', ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
}
