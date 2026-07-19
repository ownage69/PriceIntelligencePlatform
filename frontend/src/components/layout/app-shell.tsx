import { BarChart3, Boxes, Moon, Package, Store, Sun, Tag, Workflow } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useTheme } from "@/hooks/use-theme";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "/", label: "Dashboard", icon: Boxes, end: true },
  { to: "/products", label: "Products", icon: Package },
  { to: "/stores", label: "Stores", icon: Store },
  { to: "/tags", label: "Tags", icon: Tag },
  { to: "/price-history", label: "Price History", icon: BarChart3 },
  { to: "/tasks", label: "Task Monitor", icon: Workflow },
];

export function AppShell() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <aside className="fixed inset-x-0 bottom-0 z-20 border-t border-zinc-200 bg-white/90 px-3 py-2 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90 lg:inset-y-0 lg:left-0 lg:right-auto lg:w-64 lg:border-r lg:border-t-0 lg:px-4 lg:py-5">
        <div className="hidden items-center gap-2 px-2 lg:flex">
          <div className="grid size-7 place-items-center rounded-md bg-zinc-950 text-xs font-bold text-white dark:bg-zinc-50 dark:text-zinc-950">
            PI
          </div>
          <span className="text-sm font-semibold tracking-tight">Price Intelligence</span>
        </div>

        <nav className="flex items-center justify-around gap-1 lg:mt-8 lg:flex-col lg:items-stretch lg:justify-start">
          {navigation.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  "flex min-w-0 items-center gap-3 rounded-lg px-2 py-2 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-950 dark:text-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-zinc-50 lg:px-3",
                  isActive && "bg-zinc-100 text-zinc-950 dark:bg-zinc-900 dark:text-zinc-50",
                )
              }
              to={to}
            >
              <Icon className="size-4 shrink-0" />
              <span className="hidden truncate text-sm font-medium lg:block">{label}</span>
              <span className="sr-only">{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-5 left-4 right-4 hidden border-t border-zinc-200 pt-4 dark:border-zinc-800 lg:block">
          <Button className="w-full justify-start" variant="ghost" onClick={toggleTheme}>
            {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            {theme === "dark" ? "Light theme" : "Dark theme"}
          </Button>
        </div>
      </aside>
      <main className="mx-auto max-w-7xl px-4 py-7 pb-24 lg:ml-64 lg:px-8 lg:py-10 lg:pb-10">
        <Outlet />
      </main>
    </div>
  );
}
