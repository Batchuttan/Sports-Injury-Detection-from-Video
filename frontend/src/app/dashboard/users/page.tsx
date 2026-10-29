"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAdminUsers, updateUserRole, deleteUser, getAdminPlatformStats } from "@/lib/api";
import {
  Users,
  Search,
  Filter,
  ShieldAlert,
  ShieldCheck,
  Trash2,
  Edit,
  Server,
  HardDrive,
  Activity,
  CheckCircle2,
  RefreshCw,
  UserPlus
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";

const ROLES = [
  "Athlete",
  "Coach",
  "Physiotherapist",
  "Sports Scientist",
  "Administrator"
];

export default function UserManagementPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("All");
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) return;
      const [usersData, statsData] = await Promise.all([
        getAdminUsers(token),
        getAdminPlatformStats(token)
      ]);
      setUsers(usersData || []);
      setStats(statsData);
    } catch (err) {
      console.error("Failed to load admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      setUpdatingId(userId);
      const token = localStorage.getItem("token");
      if (!token) return;
      await updateUserRole(token, userId, newRole);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err: any) {
      alert("Failed to update role: " + err.message);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDeleteUser = async (userId: number, email: string) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to permanently delete user ${email} (#${userId})? All associated records will be removed.`
    );
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      await deleteUser(token, userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err: any) {
      alert("Failed to delete user: " + err.message);
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (u.sport && u.sport.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesRole = roleFilter === "All" || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold uppercase tracking-wider">
              System Administrator
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">
            User Management &amp; Platform Operations
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage athlete, coach, and clinician accounts, reassign role permissions, and monitor cloud health.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 rounded-xl text-xs font-bold transition-all flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-400" : ""}`} />
          <span>Refresh Database</span>
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Registered Users</div>
          <div className="text-3xl font-black text-white mt-1">{stats?.total_users ?? users.length}</div>
          <div className="text-[11px] text-indigo-400">Active credentials across 5 roles</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Analyses &amp; Dual Tests</div>
          <div className="text-3xl font-black text-indigo-400 mt-1">
            {(stats?.total_video_analyses ?? 0) + (stats?.total_dual_comparisons ?? 0)}
          </div>
          <div className="text-[11px] text-slate-400">
            {stats?.total_video_analyses ?? 0} single • {stats?.total_dual_comparisons ?? 0} dual runs
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <Server className="w-4 h-4 text-emerald-400" />
            <span>System Health &amp; Uptime</span>
          </div>
          <div className="text-3xl font-black text-emerald-400 mt-1">{stats?.system_health ?? "99.98%"}</div>
          <div className="text-[11px] text-slate-400">{stats?.server_status ?? "Healthy / Docker Containerized"}</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-pink-400 flex items-center gap-1.5">
            <HardDrive className="w-4 h-4 text-pink-400" />
            <span>Video Storage Used</span>
          </div>
          <div className="text-3xl font-black text-white mt-1">{stats?.storage_used_mb ?? 142} MB</div>
          <div className="text-[11px] text-pink-300">FastStart H.264 baseline optimized</div>
        </div>
      </div>

      {/* Platform Usage Chart */}
      {stats?.platform_usage_series && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            <span>Platform Usage &amp; Analytics Velocity</span>
          </h3>

          <div className="h-60 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.platform_usage_series}>
                <defs>
                  <linearGradient id="adminUsersGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="adminAnalysesGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#ec4899" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#020617",
                    borderColor: "#334155",
                    borderRadius: "0.75rem",
                    color: "#f8fafc",
                    fontSize: "12px",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Area type="monotone" dataKey="users" stroke="#3b82f6" fillOpacity={1} fill="url(#adminUsersGrad)" name="Active Accounts" />
                <Area type="monotone" dataKey="analyses" stroke="#ec4899" fillOpacity={1} fill="url(#adminAnalysesGrad)" name="Computer Vision Analyses" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by email or sport..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto flex-wrap">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs text-slate-400 font-medium">Role:</span>
          {["All", ...ROLES].map((r) => (
            <button
              key={r}
              onClick={() => setRoleFilter(r)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${roleFilter === r
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Users Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-bold text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">User ID</th>
                <th className="py-3.5 px-4">User Email</th>
                <th className="py-3.5 px-4">Assigned Role</th>
                <th className="py-3.5 px-4">Sport / Position</th>
                <th className="py-3.5 px-4">Analyses Run</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 text-xs">
                    No users matching criteria.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-slate-400 font-bold">#{u.id}</td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-white text-sm">{u.email}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <select
                        value={u.role}
                        disabled={updatingId === u.id}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="px-2.5 py-1 bg-slate-900 border border-slate-700 rounded-lg text-xs font-bold text-indigo-300 focus:outline-none focus:border-indigo-500 cursor-pointer disabled:opacity-50"
                      >
                        {ROLES.map((role) => (
                          <option key={role} value={role}>
                            {role}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-slate-300 font-medium">
                        {u.sport !== "N/A" ? `${u.sport} (${u.position})` : "General Account"}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono text-indigo-400 font-bold">{u.analyses_count}</span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleDeleteUser(u.id, u.email)}
                        className="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg transition-colors cursor-pointer"
                        title="Delete User"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
