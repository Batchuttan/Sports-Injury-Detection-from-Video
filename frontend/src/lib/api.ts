export const API_URL =
  typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "http://127.0.0.1:8000";

export const register = async (email: string, password: string, role: string) => {
  const response = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password, role }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Registration failed");
  }

  return response.json();
};

export const login = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(`${API_URL}/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    throw new Error("Invalid credentials");
  }

  return response.json();
};

export const getDeviceAccounts = async (): Promise<Array<{ email: string; role: string }>> => {
  try {
    const response = await fetch(`${API_URL}/auth/device-accounts`);
    if (!response.ok) return [];
    return await response.json();
  } catch {
    return [];
  }
};

export interface GoogleAuthResponse {
  success: boolean;
  notRegistered?: boolean;
  email?: string;
  message?: string;
  access_token?: string;
  token_type?: string;
}

export const googleLogin = async (
  email: string,
  role: string = "Athlete",
  action: "login" | "register" = "login"
): Promise<GoogleAuthResponse> => {
  const response = await fetch(`${API_URL}/auth/google`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, role, action }),
  });

  const data = await response.json().catch(() => ({}));

  if (response.status === 404) {
    return {
      success: false,
      notRegistered: true,
      email: email,
      message: data?.detail || "No registered account found for this Google email. Please register your account.",
    };
  }

  if (!response.ok) {
    return {
      success: false,
      notRegistered: false,
      email: email,
      message: data?.detail || "Google authentication failed",
    };
  }

  return {
    success: true,
    access_token: data.access_token,
    token_type: data.token_type,
  };
};

export const getMe = async (token: string) => {
  const response = await fetch(`${API_URL}/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user");
  }

  return response.json();
};

export const getAthleteProfile = async (token: string) => {
  const response = await fetch(`${API_URL}/athlete/profile`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error("Failed to fetch profile");
  }

  return response.json();
};

export const createAthleteProfile = async (token: string, profileData: Record<string, unknown>) => {
  const response = await fetch(`${API_URL}/athlete/profile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(profileData),
  });

  if (!response.ok) {
    throw new Error("Failed to create profile");
  }

  return response.json();
};

export const updateAthleteProfile = async (token: string, profileData: Record<string, unknown>) => {
  const response = await fetch(`${API_URL}/athlete/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(profileData),
  });

  if (!response.ok) {
    throw new Error("Failed to update profile");
  }

  return response.json();
};

export const uploadVideo = async (token: string, file: File, activity: string, surfaceType: string = "Unknown", footwear: string = "Unknown", rpe: number = 5, sleepQuality: number = 5) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("activity", activity);
  formData.append("surface_type", surfaceType);
  formData.append("footwear", footwear);
  formData.append("rpe", rpe.toString());
  formData.append("sleep_quality", sleepQuality.toString());

  const response = await fetch(`${API_URL}/video/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Upload failed with status:", response.status, "Details:", errorText);
    throw new Error(`Failed to upload video: ${response.status} ${errorText}`);
  }

  return response.json();
};

export const createPhysicalAssessment = async (token: string, assessmentData: Record<string, unknown>) => {
  const response = await fetch(`${API_URL}/athlete/assessments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(assessmentData),
  });
  if (!response.ok) throw new Error("Failed to create assessment");
  return response.json();
};

export const getPhysicalAssessments = async (token: string) => {
  const response = await fetch(`${API_URL}/athlete/assessments`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch assessments");
  return response.json();
};

export const createPerformanceRecord = async (token: string, recordData: Record<string, unknown>) => {
  const response = await fetch(`${API_URL}/athlete/performance`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(recordData),
  });
  if (!response.ok) throw new Error("Failed to create performance record");
  return response.json();
};

export const getPerformanceRecords = async (token: string) => {
  const response = await fetch(`${API_URL}/athlete/performance`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch performance records");
  return response.json();
};

export const getAnalyses = async (token: string, overviewOnly: boolean = false) => {
  const url = overviewOnly ? `${API_URL}/athlete/analyses?overview_only=true` : `${API_URL}/athlete/analyses`;
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch analyses");
  return response.json();
};

export const clearOverviewAnalyses = async (token: string) => {
  const response = await fetch(`${API_URL}/athlete/analyses/clear-overview`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to clear overview reports");
  return response.json();
};

export const restoreOverviewAnalyses = async (token: string) => {
  const response = await fetch(`${API_URL}/athlete/analyses/restore-overview`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to restore overview reports");
  return response.json();
};

export const deleteAnalyses = async (token: string, analysisIds: number[]) => {
  const response = await fetch(`${API_URL}/athlete/analyses/delete`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ analysis_ids: analysisIds }),
  });
  if (!response.ok) throw new Error("Failed to delete analyses");
  return response.json();
};

export const getActivityRecommendations = async (token: string, activity: string, riskLevel: string = "High Risk") => {
  const response = await fetch(`${API_URL}/recommendations/${encodeURIComponent(activity)}?risk_level=${encodeURIComponent(riskLevel)}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch activity recommendations");
  return response.json();
};

export const downloadAnalysisPdf = async (token: string, analysisId: number, filename: string = "SportsAI_Report.pdf") => {
  const response = await fetch(`${API_URL}/athlete/analyses/${analysisId}/export/pdf?token=${encodeURIComponent(token)}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to export PDF report");
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

export const downloadAnalysisCsv = async (token: string, analysisId: number, filename: string = "SportsAI_Report.xlsx", format: string = "xlsx") => {
  const response = await fetch(`${API_URL}/athlete/analyses/${analysisId}/export/csv?token=${encodeURIComponent(token)}&format=${format}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to export spreadsheet report");
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

export const getSingleAnalysis = async (token: string, analysisId: number) => {
  const response = await fetch(`${API_URL}/athlete/analyses/${analysisId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch analysis details");
  return response.json();
};

export const getNotifications = async (token: string) => {
  try {
    const response = await fetch(`${API_URL}/notifications`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return [];
    return response.json();
  } catch {
    return [];
  }
};

export const deleteNotification = async (token: string, notificationId: number) => {
  try {
    const response = await fetch(`${API_URL}/notifications/${notificationId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  } catch {
    return { success: false };
  }
};

export const clearAllNotifications = async (token: string) => {
  const response = await fetch(`${API_URL}/notifications/clear-all`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to clear notifications");
  return response.json();
};

export const forgotPassword = async (email: string) => {
  const response = await fetch(`${API_URL}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to process forgot password request.");
  }
  return response.json();
};

export const requestPasswordChange = async (token: string) => {
  const response = await fetch(`${API_URL}/auth/request-password-change`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to request password change.");
  }
  return response.json();
};

export const verifyResetToken = async (token: string) => {
  const response = await fetch(`${API_URL}/auth/verify-reset-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Invalid or expired password reset link.");
  }
  return response.json();
};

export const resetPassword = async (token: string, newPassword: string) => {
  const response = await fetch(`${API_URL}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to reset password.");
  }
  return response.json();
};

export const compareVideos = async (token: string, formData: FormData) => {
  const response = await fetch(`${API_URL}/video/compare`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Comparison failed: ${response.status} ${errorText}`);
  }
  return response.json();
};

export const compareExistingAnalyses = async (token: string, analysisIdA: number, analysisIdB: number) => {
  const response = await fetch(`${API_URL}/video/compare-existing`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      analysis_id_a: analysisIdA,
      analysis_id_b: analysisIdB,
    }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Failed to compare existing analyses.");
  }
  return response.json();
};

export const getUserSettings = async (token: string) => {
  try {
    const response = await fetch(`${API_URL}/user/settings`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      return {
        email_alerts: true,
        daily_wellness: true,
        sound_effects: false,
        profile_picture: typeof window !== "undefined" ? localStorage.getItem("user_avatar") || "" : ""
      };
    }
    return await response.json();
  } catch (err) {
    console.warn("getUserSettings connection attempt warning:", err);
    return {
      email_alerts: true,
      daily_wellness: true,
      sound_effects: false,
      profile_picture: typeof window !== "undefined" ? localStorage.getItem("user_avatar") || "" : ""
    };
  }
};

export const updateUserSettings = async (token: string, settingsData: Record<string, unknown>) => {
  const response = await fetch(`${API_URL}/user/settings`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(settingsData),
  });
  if (!response.ok) throw new Error("Failed to update user settings");
  return response.json();
};

export const uploadUserAvatar = async (token: string, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_URL}/user/avatar`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!response.ok) throw new Error("Failed to upload avatar photo");
  return response.json();
};

export const uploadUserSound = async (token: string, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_URL}/user/upload-sound`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to upload custom sound");
  }
  return response.json();
};

export const getTrainingPlans = async (token: string, includeCompleted: boolean = false, statusFilter: string = "active") => {
  const params = new URLSearchParams();
  if (includeCompleted) params.append("include_completed", "true");
  if (statusFilter) params.append("status_filter", statusFilter);
  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_URL}/training/plans${queryStr}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load training plans");
  return response.json();
};

export const getTrainingPlanDetail = async (token: string, planIdentifier: string) => {
  const response = await fetch(`${API_URL}/training/plans/${planIdentifier}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load training plan details");
  return response.json();
};

export const toggleTrainingPlanTask = async (token: string, planIdentifier: string, exerciseName: string, completed: boolean) => {
  const response = await fetch(`${API_URL}/training/plans/${planIdentifier}/toggle-task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ exercise_name: exerciseName, completed }),
  });
  if (!response.ok) throw new Error("Failed to toggle exercise task");
  return response.json();
};

export const reactivateTrainingPlan = async (token: string, planIdentifier: string) => {
  const response = await fetch(`${API_URL}/training/plans/${planIdentifier}/reactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to reactivate training plan");
  return response.json();
};

export const updateTrainingPlan = async (token: string, planIdentifier: string, updateData: Record<string, unknown>) => {
  const response = await fetch(`${API_URL}/training/plans/${planIdentifier}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updateData),
  });
  if (!response.ok) throw new Error("Failed to update training plan");
  return response.json();
};

export const getDualComparisons = async (token: string) => {
  const response = await fetch(`${API_URL}/athlete/comparisons`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch dual video comparison reports");
  return response.json();
};

export const getSingleDualComparison = async (token: string, comparisonId: number) => {
  const response = await fetch(`${API_URL}/athlete/comparisons/${comparisonId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to fetch single dual comparison detail");
  return response.json();
};

export const deleteDualComparisons = async (token: string, comparisonIds: number[]) => {
  const response = await fetch(`${API_URL}/athlete/comparisons/delete`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ comparison_ids: comparisonIds }),
  });
  if (!response.ok) throw new Error("Failed to delete dual comparison reports");
  return response.json();
};

export const downloadDualComparisonPdf = async (token: string, comparisonId: number, filename: string = "SportsAI_Dual_Report.pdf") => {
  const response = await fetch(`${API_URL}/athlete/comparisons/${comparisonId}/export/pdf?token=${encodeURIComponent(token)}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to export dual comparison PDF report");
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

export const downloadDualComparisonCsv = async (token: string, comparisonId: number, filename: string = "SportsAI_Dual_Report.xlsx", format: string = "xlsx") => {
  const response = await fetch(`${API_URL}/athlete/comparisons/${comparisonId}/export/csv?token=${encodeURIComponent(token)}&format=${format}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to export dual comparison spreadsheet report");
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

// Coach Endpoints
export const getTeamMonitoring = async (token: string) => {
  const response = await fetch(`${API_URL}/coach/team-monitoring`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load team monitoring");
  return response.json();
};

export const getWorkloadAlerts = async (token: string) => {
  const response = await fetch(`${API_URL}/coach/workload-alerts`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load workload alerts");
  return response.json();
};

// Physio Endpoints
export const getRecoveryStatus = async (token: string) => {
  const response = await fetch(`${API_URL}/physio/recovery-status`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load recovery status");
  return response.json();
};

// Sports Scientist Endpoints
export const getScientistInsights = async (token: string) => {
  const response = await fetch(`${API_URL}/scientist/biomechanical-insights`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load biomechanical insights");
  return response.json();
};

// Admin Endpoints
export const getAdminUsers = async (token: string) => {
  const response = await fetch(`${API_URL}/admin/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load users");
  return response.json();
};

export const updateUserRole = async (token: string, userId: number, role: string) => {
  const response = await fetch(`${API_URL}/admin/users/${userId}/role`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ role }),
  });
  if (!response.ok) throw new Error("Failed to update user role");
  return response.json();
};

export const deleteUser = async (token: string, userId: number) => {
  const response = await fetch(`${API_URL}/admin/users/${userId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to delete user");
  return response.json();
};

export const getAdminPlatformStats = async (token: string) => {
  const response = await fetch(`${API_URL}/admin/platform-stats`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Failed to load platform statistics");
  return response.json();
};


