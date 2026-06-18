import { cn } from "@/lib/utils";

export interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center px-6 py-14 text-center",
        className
      )}
    >
      <span
        className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-slate-400"
        aria-hidden
      >
        {icon}
      </span>
      <p className="text-sm font-semibold text-slate-900">{title}</p>
      {description ? (
        <p className="mt-1 max-w-sm text-sm text-slate-500">{description}</p>
      ) : null}
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
