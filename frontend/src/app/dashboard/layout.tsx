"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getUserFromToken } from "@/lib/auth";
import {
  LayoutDashboard,
  FileText,
  GitCompare,
  Video,
  GitBranch,
  User as UserIcon,
  Dumbbell,
  CalendarCheck,
  TrendingUp,
  Settings as SettingsIcon,
  Activity,
  Bell,
  ShieldCheck,
  Users,
  Lightbulb,
  Home as HomeIcon
} from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string>("");
  const router = useRouter();
  const pathname = usePathname();

  const [activeRole, setActiveRole] = useState<string>("");

  const syncAvatar = () => {
    const cached = localStorage.getItem("user_avatar");
    if (cached) {
      setAvatarUrl(cached);
    } else {
      setAvatarUrl("");
    }
  };

  useEffect(() => {
    const fetchedUser = getUserFromToken();
    if (!fetchedUser) {
      router.push("/");
    } else {
      setTimeout(() => {
        setUser(fetchedUser);
        const savedRole = localStorage.getItem("preview_role") || fetchedUser.role;
        setActiveRole(savedRole);
      }, 0);
      syncAvatar();
    }

    const handleRoleSwitch = (e: any) => {
      if (e.detail?.role) {
        setActiveRole(e.detail.role);
      }
    };

    const handleAvatarUpdate = () => syncAvatar();
    window.addEventListener("avatar_updated", handleAvatarUpdate);
    window.addEventListener("role_switched", handleRoleSwitch);
    return () => {
      window.removeEventListener("avatar_updated", handleAvatarUpdate);
      window.removeEventListener("role_switched", handleRoleSwitch);
    };
  }, [router]);

  if (!user) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>;
  }

  const currentRole = activeRole || user.role;

  const isLinkActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/dashboard";
    }
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  const getNavIcon = (name: string, isActive: boolean) => {
    const iconClass = `w-5 h-5 shrink-0 transition-all duration-200 ${isActive ? "text-indigo-400 scale-105" : "text-slate-400 group-hover:text-indigo-400 group-hover:scale-110"
      }`;

    switch (name) {
      case "Home":
        return <HomeIcon className={iconClass} />;
      case "My Overview":
      case "Team Overview":
      case "Platform Overview":
      case "Overview":
        return <LayoutDashboard className={iconClass} />;
      case "Recommendations":
        return <Lightbulb className={iconClass} />;
      case "Analyze Video":
        return <Video className={iconClass} />;
      case "Reports(Single Video)":
        return <FileText className={iconClass} />;
      case "Video Comparison":
        return <GitBranch className={iconClass} />;
      case "Reports(Dual Video)":
        return <GitCompare className={iconClass} />;
      case "Profile":
        return <UserIcon className={iconClass} />;
      case "My Fitness":
        return <Dumbbell className={iconClass} />;
      case "Training Plans":
        return <CalendarCheck className={iconClass} />;
      case "Progress":
        return <TrendingUp className={iconClass} />;
      case "Player Monitoring":
        return <Activity className={iconClass} />;
      case "Workload Alerts":
        return <Bell className={iconClass} />;
      case "Recovery Status":
        return <ShieldCheck className={iconClass} />;
      case "Biomechanical Analytics":
        return <TrendingUp className={iconClass} />;
      case "User Management":
        return <Users className={iconClass} />;
      case "System Settings":
      case "Settings":
        return <SettingsIcon className={iconClass} />;
      default:
        return <Activity className={iconClass} />;
    }
  };

  const getNavLinks = (role: string) => {
    switch (role) {
      case "Athlete":
        return [
          { name: "Home", href: "/dashboard" },
          { name: "Analyze Video", href: "/dashboard/upload" },
          { name: "Reports(Single Video)", href: "/dashboard/reports" },
          { name: "Video Comparison", href: "/dashboard/compare" },
          { name: "Reports(Dual Video)", href: "/dashboard/reports-dual" },
          { name: "Recommendations", href: "/dashboard/recommendations" },
          { name: "Profile", href: "/dashboard/profile" },
          { name: "My Fitness", href: "/dashboard/fitness" },
          { name: "Training Plans", href: "/dashboard/training" },
          { name: "Progress", href: "/dashboard/progress" },
        ];
      case "Coach":
        return [
          { name: "Home", href: "/dashboard" },
          { name: "Analyze Video", href: "/dashboard/upload" },
          { name: "Reports(Single Video)", href: "/dashboard/reports" },
          { name: "Video Comparison", href: "/dashboard/compare" },
          { name: "Reports(Dual Video)", href: "/dashboard/reports-dual" },
          { name: "Player Monitoring", href: "/dashboard/monitoring" },
          { name: "Workload Alerts", href: "/dashboard/workload" },
        ];
      case "Physiotherapist":
        return [
          { name: "Home", href: "/dashboard" },
          { name: "Analyze Video", href: "/dashboard/upload" },
          { name: "Reports(Single Video)", href: "/dashboard/reports" },
          { name: "Video Comparison", href: "/dashboard/compare" },
          { name: "Reports(Dual Video)", href: "/dashboard/reports-dual" },
          { name: "Recovery Status", href: "/dashboard/recovery" },
          { name: "Recommendations", href: "/dashboard/recommendations" },
          { name: "Training Plans", href: "/dashboard/training" },
        ];
      case "Sports Scientist":
        return [
          { name: "Home", href: "/dashboard" },
          { name: "Analyze Video", href: "/dashboard/upload" },
          { name: "Reports(Single Video)", href: "/dashboard/reports" },
          { name: "Video Comparison", href: "/dashboard/compare" },
          { name: "Reports(Dual Video)", href: "/dashboard/reports-dual" },
          { name: "Biomechanical Analytics", href: "/dashboard/analytics" },
          { name: "Progress", href: "/dashboard/progress" },
        ];
      case "Administrator":
        return [
          { name: "Home", href: "/dashboard" },
          { name: "Analyze Video", href: "/dashboard/upload" },
          { name: "Reports(Single Video)", href: "/dashboard/reports" },
          { name: "Video Comparison", href: "/dashboard/compare" },
          { name: "Reports(Dual Video)", href: "/dashboard/reports-dual" },
          { name: "User Management", href: "/dashboard/users" },
          { name: "System Settings", href: "/dashboard/settings" },
        ];
      default:
        return [
          { name: "Home", href: "/dashboard" },
          { name: "Analyze Video", href: "/dashboard/upload" },
          { name: "Reports(Single Video)", href: "/dashboard/reports" },
          { name: "Video Comparison", href: "/dashboard/compare" },
          { name: "Reports(Dual Video)", href: "/dashboard/reports-dual" },
        ];
    }
  };

  const navLinks = getNavLinks(currentRole);

  return (
    <div className="flex min-h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950/50 hidden md:flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800">
          <span className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-500">
            SportsAI
          </span>
        </div>

        <nav className="flex-1 py-6 px-4 space-y-2 overflow-y-auto">
          {navLinks.map((link, idx) => {
            const isActive = isLinkActive(link.href);
            return (
              <Link
                key={idx}
                href={link.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 group border cursor-pointer ${isActive
                  ? "bg-gradient-to-r from-indigo-600/25 via-indigo-500/20 to-pink-600/15 text-white font-bold border-indigo-500/40 shadow-[0_0_20px_rgba(99,102,241,0.25)]"
                  : "border-transparent text-slate-400 hover:text-white hover:bg-slate-900/90 hover:border-slate-700/80 hover:shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                  }`}
              >
                {getNavIcon(link.name, isActive)}
                <span className="truncate">{link.name}</span>
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-pink-400 shadow-[0_0_8px_rgba(244,114,182,0.8)] animate-pulse" />
                )}
              </Link>
            );
          })}
          {(() => {
            const isSettingsActive = isLinkActive("/dashboard/settings");
            return (
              <Link
                href="/dashboard/settings"
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 group border cursor-pointer ${isSettingsActive
                  ? "bg-gradient-to-r from-indigo-600/25 via-indigo-500/20 to-pink-600/15 text-white font-bold border-indigo-500/40 shadow-[0_0_20px_rgba(99,102,241,0.25)]"
                  : "border-transparent text-slate-400 hover:text-white hover:bg-slate-900/90 hover:border-slate-700/80 hover:shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                  }`}
              >
                <SettingsIcon
                  className={`w-5 h-5 shrink-0 transition-all duration-200 ${isSettingsActive ? "text-indigo-400 scale-105" : "text-slate-400 group-hover:text-indigo-400 group-hover:scale-110"
                    }`}
                />
                <span>Settings</span>
                {isSettingsActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-pink-400 shadow-[0_0_8px_rgba(244,114,182,0.8)] animate-pulse" />
                )}
              </Link>
            );
          })()}
        </nav>

        <div className="p-6 border-t border-slate-800">
          <Link href="/dashboard/settings" className="flex items-center gap-3 group hover:opacity-90 transition-opacity">
            {avatarUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={avatarUrl}
                alt="Profile"
                className="w-10 h-10 rounded-full object-cover border border-indigo-500/60 shadow-[0_0_10px_rgba(99,102,241,0.25)]"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-pink-500 flex items-center justify-center text-white font-bold text-sm shadow-[0_0_10px_rgba(99,102,241,0.25)]">
                {user.email.substring(0, 2).toUpperCase()}
              </div>
            )}
            <div className="overflow-hidden">
              <div className="text-sm font-medium text-slate-200 truncate group-hover:text-white transition-colors">{user.email}</div>
              <div className="text-xs text-slate-500 flex items-center gap-1">
                <span>{user.role}</span>
                <span className="text-[10px] text-indigo-400 font-mono">• Settings</span>
              </div>
            </div>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-800 bg-slate-950/50 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold capitalize text-white">{currentRole} Dashboard</h2>
            <div className="flex items-center gap-2 bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-1 shadow-sm">
              <span className="text-xs text-slate-400 font-medium">Role View:</span>
              <select
                value={currentRole}
                onChange={(e) => {
                  const newRole = e.target.value;
                  setActiveRole(newRole);
                  localStorage.setItem("preview_role", newRole);
                  window.dispatchEvent(new CustomEvent("role_switched", { detail: { role: newRole } }));
                }}
                className="bg-transparent text-xs font-bold text-indigo-400 focus:outline-none cursor-pointer"
              >
                <option value="Athlete" className="bg-slate-900 text-slate-200">Athlete</option>
                <option value="Coach" className="bg-slate-900 text-slate-200">Coach</option>
                <option value="Physiotherapist" className="bg-slate-900 text-slate-200">Physiotherapist</option>
                <option value="Sports Scientist" className="bg-slate-900 text-slate-200">Sports Scientist</option>
                <option value="Administrator" className="bg-slate-900 text-slate-200">Administrator</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-slate-200 transition-colors relative">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-pink-500 rounded-full border-2 border-slate-950"></span>
            </button>
            <button onClick={() => { localStorage.removeItem("token"); router.push("/"); }} className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
              Log Out
            </button>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-8 relative">
          <div className="absolute top-0 right-0 w-[40%] h-[40%] bg-indigo-500/10 blur-[100px] pointer-events-none" />
          {children}
        </div>
      </main>
    </div>
  );
}
