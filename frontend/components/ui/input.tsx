'use client';

import * as React from 'react';
import { Eye, EyeOff, X, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  isSuccess?: boolean;
  onClear?: () => void;
}

export function Input({
  label,
  error,
  isSuccess,
  type = 'text',
  value,
  onChange,
  onClear,
  className = '',
  id,
  ...props
}: InputProps) {
  const [isFocused, setIsFocused] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);
  const internalId = React.useId();
  const inputId = id || internalId;

  const isPassword = type === 'password';
  const currentType = isPassword ? (showPassword ? 'text' : 'password') : type;
  const isFilled = value !== undefined && value !== null && String(value).length > 0;

  return (
    <div className={`relative w-full flex flex-col gap-1.5 ${className}`}>
      <div
        className={`relative w-full rounded-[16px] border bg-surface-primary transition-all duration-180 ${
          error
            ? 'border-danger focus-within:ring-2 focus-within:ring-danger/20'
            : isSuccess
            ? 'border-success focus-within:ring-2 focus-within:ring-success/20'
            : 'border-border-custom focus-within:border-accent-primary focus-within:ring-2 focus-within:ring-accent-primary/20'
        }`}
      >
        <input
          id={inputId}
          type={currentType}
          value={value}
          onChange={onChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder=" "
          className="w-full px-4 pt-6 pb-2 text-text-primary bg-transparent rounded-[16px] outline-hidden text-base placeholder-transparent transition-all duration-180"
          {...props}
        />
        
        {/* Floating Label */}
        <label
          htmlFor={inputId}
          className={`absolute left-4 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none origin-left transition-all duration-180 ${
            isFocused || isFilled
              ? 'scale-75 -translate-y-4 text-accent-primary'
              : 'scale-100 translate-y-[-50%] text-text-muted'
          }`}
        >
          {label}
        </label>

        {/* Action icons */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-text-muted">
          {onClear && isFilled && !isPassword && (
            <button
              type="button"
              onClick={onClear}
              className="p-1 hover:text-text-primary rounded-full transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}

          {isPassword && isFilled && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="p-1 hover:text-text-primary rounded-full transition-colors"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          )}
        </div>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            className="flex items-center gap-1 text-danger text-sm px-1"
          >
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
