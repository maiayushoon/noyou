import {
  LayoutDashboard,
  MessageSquareText,
  Sparkles,
  TrendingUp,
  Bell,
  Brush,
  ShieldCheck,
  UserRound,
  CreditCard,
  BarChart3,
  Users,
  Link2,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** Show a small "AI" badge on the item. */
  ai?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Overview", href: "/", icon: LayoutDashboard },
  { label: "Mentions", href: "/mentions", icon: MessageSquareText },
  { label: "Pre-Post Check", href: "/predict", icon: ShieldCheck, ai: true },
  { label: "AI Visibility", href: "/ai-visibility", icon: Sparkles, ai: true },
  { label: "Alerts", href: "/alerts", icon: Bell },
  { label: "Cleanup", href: "/cleanup", icon: Brush },
  { label: "Benchmark", href: "/benchmark", icon: BarChart3 },
  { label: "Trends", href: "/trends", icon: TrendingUp },
  { label: "Teams", href: "/teams", icon: Users },
  { label: "Connections", href: "/connections", icon: Link2 },
  { label: "Accounts", href: "/accounts", icon: UserRound },
  { label: "Billing", href: "/billing", icon: CreditCard },
];
