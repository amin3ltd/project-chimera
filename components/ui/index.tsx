import React from 'react';

type ClassValue = string | undefined | null | false;

function cn(...values: ClassValue[]): string {
  return values.filter(Boolean).join(' ');
}

type BaseProps = React.HTMLAttributes<HTMLElement> & { className?: string };

export function Card(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div
      className={cn(
        'rounded-2xl border bg-white shadow-[0_1px_0_rgba(15,23,42,0.04)]',
        'backdrop-blur supports-[backdrop-filter]:bg-white/80',
        className
      )}
      {...rest}
    />
  );
}

export function CardHeader(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return <div className={cn('flex flex-col px-5 pt-5', className)} {...rest} />;
}

export function CardTitle(props: React.HTMLAttributes<HTMLHeadingElement>) {
  const { className, ...rest } = props;
  return (
    <h3 className={cn('font-semibold tracking-tight text-slate-900', className)} {...rest} />
  );
}

export function CardContent(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return <div className={cn('px-5 pb-5', className)} {...rest} />;
}

type BadgeVariant = 'default' | 'outline';

export function Badge(
  props: React.HTMLAttributes<HTMLSpanElement> & { variant?: BadgeVariant }
) {
  const { className, variant = 'default', ...rest } = props;
  const base =
    'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold leading-none';
  const styles =
    variant === 'outline'
      ? 'border border-slate-200 bg-white text-slate-700'
      : 'bg-slate-900 text-white';
  return <span className={cn(base, styles, className)} {...rest} />;
}

type ButtonVariant = 'default' | 'outline' | 'ghost' | 'destructive';
type ButtonSize = 'sm' | 'md';

export function Button(
  props: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    size?: ButtonSize;
  }
) {
  const { className, variant = 'default', size = 'md', disabled, ...rest } = props;

  const base =
    'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors';
  const focus =
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/50 focus-visible:ring-offset-2';
  const sizes = size === 'sm' ? 'h-9 px-3 text-sm' : 'h-10 px-4 text-sm';

  const variants: Record<ButtonVariant, string> = {
    default: 'bg-slate-900 text-white hover:bg-slate-800',
    outline: 'border border-slate-200 bg-white text-slate-900 hover:bg-slate-50',
    ghost: 'bg-transparent text-slate-700 hover:bg-slate-100',
    destructive: 'bg-rose-600 text-white hover:bg-rose-700',
  };

  const disabledStyles = disabled ? 'opacity-60 cursor-not-allowed hover:bg-inherit' : '';

  return (
    <button
      className={cn(base, focus, sizes, variants[variant], disabledStyles, className)}
      disabled={disabled}
      {...rest}
    />
  );
}

export function Textarea(
  props: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { className?: string }
) {
  const { className, ...rest } = props;
  return (
    <textarea
      className={cn(
        'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900',
        'placeholder:text-slate-400 shadow-sm',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 focus-visible:ring-offset-2',
        className
      )}
      {...rest}
    />
  );
}

export function Input(
  props: React.InputHTMLAttributes<HTMLInputElement> & { className?: string }
) {
  const { className, ...rest } = props;
  return (
    <input
      className={cn(
        'h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900',
        'placeholder:text-slate-400 shadow-sm',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 focus-visible:ring-offset-2',
        className
      )}
      {...rest}
    />
  );
}

export function Separator(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return <div className={cn('h-px w-full bg-slate-200', className)} {...rest} />;
}

export function Progress(props: { value: number; className?: string }) {
  const value = Math.max(0, Math.min(100, props.value));
  return (
    <div className={cn('h-2 w-full rounded-full bg-slate-100', props.className)}>
      <div
        className="h-2 rounded-full bg-emerald-500"
        style={{ width: `${value}%` }}
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={100}
        role="progressbar"
      />
    </div>
  );
}

