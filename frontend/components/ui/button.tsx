'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2 } from 'lucide-react';

interface ButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onDrag' | 'onDragStart' | 'onDragEnd' | 'onDragOver' | 'onDragEnter' | 'onDragLeave' | 'onDragExit' | 'onAnimationStart'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  isLoading?: boolean;
  isSuccess?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  children,
  variant = 'primary',
  isLoading = false,
  isSuccess = false,
  size = 'md',
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const baseStyle =
    'relative inline-flex items-center justify-center font-medium transition-all duration-200 rounded-[14px] outline-hidden focus:ring-2 focus:ring-accent-primary/50 cursor-pointer disabled:cursor-not-allowed select-none overflow-hidden';

  const variantStyles = {
    primary:
      'bg-accent-primary text-white shadow-md shadow-accent-primary/20 hover:shadow-lg hover:shadow-accent-primary/30 active:shadow-sm border border-transparent',
    secondary:
      'bg-surface-secondary text-text-primary border border-border-custom hover:bg-surface-elevated hover:border-border-hover shadow-sm',
    ghost:
      'bg-transparent text-text-secondary hover:bg-surface-secondary hover:text-text-primary border border-transparent',
    danger:
      'bg-danger text-white hover:bg-danger/90 shadow-md shadow-danger/20 hover:shadow-lg hover:shadow-danger/30 border border-transparent',
  };

  const sizeStyles = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-5 py-3 text-base',
    lg: 'px-7 py-4 text-lg',
  };

  return (
    <motion.button
      whileHover={{ y: -2, scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className={`${baseStyle} ${variantStyles[variant]} ${sizeStyles[size]} ${
        disabled || isLoading ? 'opacity-60 cursor-not-allowed' : ''
      } ${className}`}
      disabled={disabled || isLoading || isSuccess}
      {...props}
    >
      <span className="flex items-center gap-2 justify-center">
        {isLoading && (
          <Loader2 className="h-4 w-4 animate-spin text-current shrink-0" />
        )}
        {isSuccess && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 15 }}
          >
            <Check className="h-4 w-4 text-success shrink-0" />
          </motion.span>
        )}
        <span className={isLoading || isSuccess ? 'opacity-90' : ''}>
          {children}
        </span>
      </span>
    </motion.button>
  );
}
