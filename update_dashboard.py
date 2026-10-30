import os

page_path = r"c:\Users\User\OneDrive\Desktop\INTERNSHIPS\Infosys Springboot\Sports Injury Detection from Video\frontend\src\app\dashboard\page.tsx"

with open(page_path, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "      {/* KPI Cards */}"
end_marker = "      })()}\n    </div>\n  );\n}\n\nfunction PhysioDashboard()"

new_body = """      {/* Top Overall KPI Intelligence Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* KPI 1: Average Risk Score */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Average Risk Score
            </span>
            <span
              className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold border ${
                avgRiskScore > 35
                  ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                  : avgRiskScore > 20
                  ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                  : "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
              }`}
            >
              {avgRiskScore <= 20 ? "Optimal Efficiency" : avgRiskScore <= 35 ? "Moderate Caution" : "Joint Strain Detected"}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <div className={`text-4xl font-black ${avgRiskScore > 35 ? "text-rose-400" : avgRiskScore > 20 ? "text-amber-400" : "text-emerald-400"}`}>
              {avgRiskScore}
            </div>
            <span className="text-slate-500 font-semibold text-sm">/ 100</span>
          </div>

          <div className="text-xs text-slate-400">
            Based on <strong className="text-slate-200">{totalCount}</strong> recent movement analyses
          </div>

          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                avgRiskScore > 35
                  ? "bg-gradient-to-r from-amber-500 to-rose-500"
                  : "bg-gradient-to-r from-emerald-500 to-indigo-500"
              }`}
              style={{ width: `${Math.min(100, Math.max(5, avgRiskScore))}%` }}
            />
          </div>
        </div>

        {/* KPI 2: Total Videos Analyzed */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Videos Analyzed
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-semibold font-mono">
              100% Computer Vision
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-black text-white">
              {totalCount}
            </div>
            <span className="text-xs text-slate-500">Evaluations</span>
          </div>

          <div className="text-xs text-slate-400">
            Historical kinetic motion evaluations
          </div>

          <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-400">
            <span className="text-emerald-400 font-bold">{lowRiskAnalyses.length} Safe</span>
            <span>•</span>
            <span className="text-amber-400 font-bold">{moderateRiskAnalyses.length} Moderate</span>
            <span>•</span>
            <span className="text-rose-400 font-bold">{highRiskAnalyses.length} High Risk</span>
          </div>
        </div>

        {/* KPI 3: Run New Video Analysis CTA */}
        <Link
          href="/dashboard/upload"
          className="glass-panel p-6 rounded-2xl border-indigo-500/40 bg-gradient-to-br from-indigo-500/15 via-indigo-600/10 to-pink-500/10 hover:from-indigo-500/25 hover:to-pink-500/20 transition-all cursor-pointer flex flex-col justify-between group shadow-[0_0_25px_rgba(79,70,229,0.2)] border"
        >
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-300 flex items-center justify-center border border-indigo-500/30 group-hover:scale-110 group-hover:bg-indigo-500 group-hover:text-white transition-all shadow-md">
              <Video className="w-5 h-5" />
            </div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-pink-400 bg-pink-500/10 px-2 py-0.5 rounded-full border border-pink-500/20">
              Instant AI
            </span>
          </div>

          <div className="my-2">
            <div className="text-base font-extrabold text-white group-hover:text-indigo-200 transition-colors flex items-center gap-1.5">
              <span>Run New Video Analysis</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
            <div className="text-xs text-slate-400 mt-0.5">
              Autonomous 8-Action kinetic inspection
            </div>
          </div>

          <div className="text-[11px] text-indigo-400 font-medium">
            Jump, Sprint, Squat, Throw, Cut & Drills &rarr;
          </div>
        </Link>

        {/* KPI 4: Kinetic Readiness Index */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Kinetic Readiness Index
            </span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>

          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-black text-emerald-400">
              {readinessIndex}%
            </div>
            <span className="text-xs text-slate-400">Recovery & Form Readiness</span>
          </div>

          <div className="text-xs text-slate-400">
            Calculated from dynamic stability, joint angle deltas, and symmetry
          </div>

          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-700"
              style={{ width: `${readinessIndex}%` }}
            />
          </div>
        </div>

        {/* KPI 5: Clean Technique Ratio */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Movement Form Compliance
            </span>
            <CheckCircle2 className="w-4 h-4 text-indigo-400" />
          </div>

          <div className="flex items-baseline gap-2">
            <div className="text-4xl font-black text-white">
              {cleanTechniquePercent}%
            </div>
            <span className="text-xs text-slate-400">Optimal Form Ratio</span>
          </div>

          <div className="text-xs text-slate-400">
            {lowRiskAnalyses.length} clean sessions with zero acute joint collapse
          </div>

          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3">
            <div
              className="h-full bg-gradient-to-r from-pink-500 via-indigo-500 to-emerald-400 rounded-full transition-all duration-700"
              style={{ width: `${cleanTechniquePercent}%` }}
            />
          </div>
        </div>

        {/* KPI 6: Primary Vulnerability Focus */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Primary Vulnerability Focus
            </span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>

          <div className="text-lg font-black text-rose-300 truncate">
            {Object.entries(anomalyCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "Knee Valgus / ACL"}
          </div>

          <div className="text-xs text-slate-400">
            Detected across {Object.entries(anomalyCounts).sort((a, b) => b[1] - a[1])[0]?.[1] || 0} historical assessment flags
          </div>

          <div className="pt-2">
            <Link
              href="/dashboard/recommendations"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-bold inline-flex items-center gap-1"
            >
              <span>Explore Targeted Prescriptions</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Section: Full Kinetic Chain Overall Joint Telemetry */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              <span>Full Kinetic Chain Overall Biomechanical Telemetry</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Cumulative averages synthesized across all microscopic joint angles, velocities, and rotational sway
            </p>
          </div>
          <span className="text-xs font-mono bg-slate-900 text-slate-300 px-3 py-1 rounded-lg border border-slate-800">
            {totalCount} Sessions Aggregated
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Valgus */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Mean Peak Knee Valgus
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-black ${Number(avgValgus) > 15 ? "text-rose-400" : "text-emerald-400"}`}>
                {avgValgus}°
              </span>
              <span className="text-[11px] text-slate-500 font-normal">Normal &lt; 15.0°</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              {Number(avgValgus) > 15
                ? "Medial collapse tendency during deceleration touchdown."
                : "Safe frontal plane knee alignment maintained."}
            </p>
          </div>

          {/* Trunk Lean */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Mean Trunk / Spine Sway
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-black ${Number(avgTrunkLean) > 25 ? "text-amber-400" : "text-slate-200"}`}>
                {avgTrunkLean}°
              </span>
              <span className="text-[11px] text-slate-500 font-normal">Normal &lt; 25.0°</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Torso lean stability and lumbar postural alignment across explosive movements.
            </p>
          </div>

          {/* Ankle Velocity */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Ankle Propulsion Velocity
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-pink-400">
                {avgAnkleVel} <span className="text-xs font-normal text-slate-400">m/s</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Average ground flight clearance: <strong className="text-indigo-300">{avgFlight}%</strong> above turf.
            </p>
          </div>

          {/* Bilateral Symmetry */}
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Bilateral Kinetic Symmetry
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-indigo-400">
                {avgSymmetry}%
              </span>
              <span className="text-[11px] text-slate-500 font-normal">Optimal Balance</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-tight">
              Left vs Right limb velocity and joint moment distribution equality.
            </p>
          </div>
        </div>
      </div>

      {/* Section: 8-Action Kinetic Mastery Matrix */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              <span>8-Action Kinetic Mastery & Movement Profile Distribution</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Historical summary of athlete compliance and risk ratings across all targeted sports movements
            </p>
          </div>
          <Link
            href="/dashboard/recommendations"
            className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1"
          >
            <span>View All Movement Prescriptions</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {ALL_8_ACTIONS.map((action) => {
            const data = activityMap[action];
            const count = data?.count || 0;
            const avgActRisk = count > 0 ? Math.round(data.totalRisk / count) : null;
            const isEvaluated = count > 0;

            return (
              <div
                key={action}
                className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/90 hover:border-slate-700 transition-all flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm text-white">{action}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                        !isEvaluated
                          ? "bg-slate-800 text-slate-400 border-slate-700"
                          : avgActRisk! > 35
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                          : avgActRisk! > 20
                          ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                          : "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                      }`}
                    >
                      {!isEvaluated ? "No Data" : `${avgActRisk} Risk`}
                    </span>
                  </div>

                  <div className="text-xs text-slate-400">
                    {isEvaluated ? (
                      <span>
                        <strong className="text-white">{count}</strong> videos assessed
                      </span>
                    ) : (
                      "Awaiting first video"
                    )}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800/80">
                  {isEvaluated ? (
                    <Link
                      href={`/dashboard/recommendations?activity=${encodeURIComponent(action)}&risk=${
                        avgActRisk! > 35 ? "High%20Risk" : avgActRisk! > 20 ? "Moderate%20Risk" : "Low%20Risk"
                      }`}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-bold inline-flex items-center gap-1 group"
                    >
                      <span>Prescriptions</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </Link>
                  ) : (
                    <Link
                      href="/dashboard/upload"
                      className="text-xs text-slate-500 hover:text-slate-300 inline-flex items-center gap-1"
                    >
                      <span>Upload Video &rarr;</span>
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Section: Longitudinal Risk Score Trajectory */}
      {trajectoryData.length > 1 && (
        <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-400" />
                <span>Historical Movement Risk Score Trajectory</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Progression of biomechanical risk across chronological analysis sessions
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-indigo-300">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                <span>Session Risk Score</span>
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-0.5 bg-rose-500" />
                <span>Risk Threshold (35 pts)</span>
              </span>
            </div>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trajectoryData}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="session" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    borderRadius: "12px",
                    color: "#f8fafc",
                    fontSize: "12px",
                  }}
                  formatter={(val: any) => [`${val} / 100 Risk`, "Session Score"]}
                  labelFormatter={(lbl) => `Session ${lbl}`}
                />
                <Area
                  type="monotone"
                  dataKey="risk"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorRisk)"
                />
                <Line
                  type="monotone"
                  dataKey="safetyThreshold"
                  stroke="#f43f5e"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Section: Clinical Directives & Corrective Action Hub */}
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>AI Clinical Directives & Biomechanical Priorities</span>
          </h3>
          <span className="text-xs text-indigo-400 font-mono">Personalized Formulation</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
              1. Frontal Knee Valgus Control
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Incorporate banded lateral monster walks and single-leg squats to strengthen the gluteus medius and prevent inward knee collapse.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-pink-400 uppercase tracking-wider">
              2. Eccentric Deceleration Loading
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Perform single-leg Romanian deadlifts and Nordic curls to build eccentric hamstring capacity and absorb anterior tibial shear forces.
            </p>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
              3. Core & Thoracic Symmetry
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Integrate rotational medicine ball throws and anti-rotational Pallof presses to mitigate trunk sway during high-velocity cutting.
            </p>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-400">
            For individual microscopic joint telemetry, frame overlays, and PDF/CSV downloads, visit the permanent Reports tab.
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard/recommendations"
              className="text-xs font-bold text-white hover:text-indigo-300 transition-colors flex items-center gap-1"
            >
              <span>Explore Recommendations</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <span className="text-slate-600">•</span>
            <Link
              href="/dashboard/training"
              className="text-xs font-bold text-white hover:text-pink-300 transition-colors flex items-center gap-1"
            >
              <span>Training Plans</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <span className="text-slate-600">•</span>
            <Link
              href="/dashboard/reports"
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
            >
              <span>Reports Archive</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function PhysioDashboard()"""

pos1 = content.find(start_marker)
pos2 = content.find(end_marker)

if pos1 == -1:
    print(f"Error: start_marker not found! '{start_marker}'")
elif pos2 == -1:
    print(f"Error: end_marker not found! '{end_marker}'")
else:
    print(f"Found markers: pos1={pos1}, pos2={pos2}")
    new_content = content[:pos1] + new_body + content[pos2 + len(end_marker):]
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated page.tsx!")
