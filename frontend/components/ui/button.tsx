"use client";

import { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type ButtonVariant =
  | "primary"
  | "ai"
  | "secondary"
  | "outline"
  | "ghost"
  | "danger";
export type ButtonSize = "sm" | "md" | "lg" | "icon";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const VARIANTS: Record<ButtonVariant, string> = {
  primary:
    "bg-slate-900 text-white shadow-sm hover:bg-slate-800 active:bg-slate-900",
  ai: "bg-ai-gradient text-white shadow-ai hover:brightness-[1.06] active:brightness-100",
  secondary:
    "bg-slate-100 text-slate-900 hover:bg-slate-200 active:bg-slate-100",
  outline:
    "border border-hairline bg-white text-slate-700 shadow-sm hover:bg-slate-50 hover:text-slate-900",
  ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  danger: "bg-red-600 text-white shadow-sm hover:bg-red-700 active:bg-red-600",
};

const SIZES: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-sm gap-1.5 rounded-lg",
  md: "h-10 px-4 text-sm gap-2 rounded-lg",
  lg: "h-11 px-5 text-[0.95rem] gap-2 rounded-xl",
  icon: "h-9 w-9 rounded-lg",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      loading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex select-none items-center justify-center whitespace-nowrap font-medium transition-all duration-150",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ai-indigo",
          "disabled:cursor-not-allowed disabled:opacity-55",
          VARIANTS[variant],
          SIZES[size],
          className
        )}
        {...props}
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
        ) : (
          leftIcon
        )}
        {children}
        {!loading ? rightIcon : null}
      </button>
    );
  }
);
Button.displayName = "Button";
