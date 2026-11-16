export const getUserFromToken = () => {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const decoded = JSON.parse(atob(parts[1]));
    // Check if token has expired
    if (decoded.exp && decoded.exp * 1000 < Date.now()) {
      clearSession();
      return null;
    }
    return {
      email: decoded.sub,
      role: decoded.role
    };
  } catch {
    return null;
  }
};

export const clearSession = () => {
  if (typeof window === "undefined") return;
  localStorage.removeItem("token");
  localStorage.removeItem("preview_role");
  localStorage.removeItem("user_avatar");
  localStorage.removeItem("sound_effects");
};
