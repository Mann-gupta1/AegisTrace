"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Clock,
  FileText,
  Home,
  Search,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/runs", label: "Runs", icon: Activity },
  { href: "/retrieval", label: "Retrieval Quality", icon: Search },
  { href: "/tokens", label: "Token Analytics", icon: Zap },
  { href: "/latency", label: "Latency", icon: Clock },
  { href: "/prompts", label: "Prompts", icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border bg-card">
      <div className="flex h-16 items-center gap-2 border-b border-border px-6">
        <BarChart3 className="h-6 w-6 text-accent" />
        <span className="text-lg font-semibold tracking-tight">AegisTrace</span>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent/15 text-accent"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border px-6 py-4">
        <p className="text-xs text-muted-foreground">AegisTrace v1.0</p>
        <p className="text-xs text-muted-foreground">Observability Platform</p>
      </div>
    </aside>
  );
}
