"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  CheckCircle2,
  Info,
  TriangleAlert,
  XCircle,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type ToastVariant = "success" | "error" | "info" | "warning";

interface Toast {
  id: number;
  variant: ToastVariant;
  title: string;
  description?: string;
}

interface ToastContextValue {
  toast: (input: {
    variant?: ToastVariant;
    title: string;
    description?: string;
  }) => void;
  success: (title: string, description?: string) => void;
  error: (title: string, description?: string) => void;
  info: (title: string, description?: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let counter = 0;

const ICONS: Record<ToastVariant, typeof CheckCircle2> = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
  warning: TriangleAlert,
};

const ACCENT: Record<ToastVariant, string> = {
  success: "text-emerald-500",
  error: "text-red-500",
  info: "text-ai-indigo",
  warning: "text-amber-500",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (input: { variant?: ToastVariant; title: string; description?: string }) => {
      const id = ++counter;
      const variant = input.variant ?? "info";
      setToasts((prev) => [
        ...prev,
        { id, variant, title: input.title, description: input.description },
      ]);
      window.setTimeout(() => dismiss(id), 4200);
    },
    [dismiss]
  );

  const value = useMemo<ToastContextValue>(
    () => ({
      toast: push,
      success: (title, description) =>
        push({ variant: "success", title, description }),
      error: (title, description) =>
        push({ variant: "error", title, description }),
      info: (title, description) =>
        push({ variant: "info", title, description }),
    }),
    [push]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Toaster toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

function Toaster({
  toasts,
  onDismiss,
}: {
  toasts: Toast[];
  onDismiss: (id: number) => void;
}) {
  return (
    <div
      className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2"
      aria-live="polite"
      aria-atomic="true"
    >
      <AnimatePresence initial={false}>
        {toasts.map((t) => {
          const Icon = ICONS[t.variant];
          return (
            <motion.div
              key={t.id}
              layout
              initial={{ opacity: 0, y: 12, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8, scale: 0.96 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="pointer-events-auto flex items-start gap-3 rounded-xl border border-hairline bg-white p-3.5 shadow-card"
              role="status"
            >
              <Icon className={cn("mt-0.5 h-5 w-5 shrink-0", ACCENT[t.variant])} />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-900">{t.title}</p>
                {t.description ? (
                  <p className="mt-0.5 text-sm text-slate-500">{t.description}</p>
                ) : null}
              </div>
              <button
                type="button"
                onClick={() => onDismiss(t.id)}
                aria-label="Dismiss notification"
                className="shrink-0 rounded-md p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within a <ToastProvider>");
  }
  return ctx;
}
