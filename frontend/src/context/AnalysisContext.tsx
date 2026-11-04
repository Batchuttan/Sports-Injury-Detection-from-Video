"use client";

import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { uploadVideo, compareVideos, compareExistingAnalyses } from "@/lib/api";
import { playAudioCue } from "@/lib/audioCue";

export interface ActiveNotification {
  id: string;
  type: "single" | "dual";
  title: string;
  message: string;
  link: string;
  linkText: string;
  timestamp: number;
}

interface AnalysisContextType {
  // Single Video State
  isAnalyzingSingle: boolean;
  singleProgress: number;
  singleStage: string;
  singleFileName: string;
  singleResult: any | null;
  singleError: string | null;
  startSingleAnalysis: (
    token: string,
    file: File,
    activity: string,
    surfaceType: string,
    footwear: string,
    rpe: number,
    sleepQuality: number
  ) => Promise<any>;
  clearSingleResult: () => void;
  resetSingleError: () => void;

  // Dual Video Comparison State
  isComparingDual: boolean;
  dualProgress: number;
  dualStage: string;
  dualFileAName: string;
  dualFileBName: string;
  dualResult: any | null;
  dualError: string | null;
  startDualUploadCompare: (
    token: string,
    formData: FormData,
    fileAName: string,
    fileBName: string
  ) => Promise<any>;
  startDualExistingCompare: (
    token: string,
    idA: number,
    idB: number,
    nameA: string,
    nameB: string
  ) => Promise<any>;
  clearDualResult: () => void;
  resetDualError: () => void;

  // Settings & Notification Controls
  showProgressBadge: boolean;
  setShowProgressBadge: (show: boolean) => void;
  activeNotification: ActiveNotification | null;
  dismissNotification: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Single Video State
  const [isAnalyzingSingle, setIsAnalyzingSingle] = useState(false);
  const [singleProgress, setSingleProgress] = useState(0);
  const [singleStage, setSingleStage] = useState("");
  const [singleFileName, setSingleFileName] = useState("");
  const [singleResult, setSingleResult] = useState<any | null>(null);
  const [singleError, setSingleError] = useState<string | null>(null);

  // Dual Video State
  const [isComparingDual, setIsComparingDual] = useState(false);
  const [dualProgress, setDualProgress] = useState(0);
  const [dualStage, setDualStage] = useState("");
  const [dualFileAName, setDualFileAName] = useState("");
  const [dualFileBName, setDualFileBName] = useState("");
  const [dualResult, setDualResult] = useState<any | null>(null);
  const [dualError, setDualError] = useState<string | null>(null);

  // Notification & Settings
  const [showProgressBadge, setShowProgressBadgeState] = useState(true);
  const [activeNotification, setActiveNotification] = useState<ActiveNotification | null>(null);

  const singleTimerRef = useRef<NodeJS.Timeout | null>(null);
  const dualTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Sync showProgressBadge from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("show_progress_badge");
      if (stored !== null) {
        setShowProgressBadgeState(stored === "true" || stored === "1");
      }
    }
  }, []);

  const setShowProgressBadge = (show: boolean) => {
    setShowProgressBadgeState(show);
    if (typeof window !== "undefined") {
      localStorage.setItem("show_progress_badge", String(show));
    }
  };

  const triggerAudioChime = () => {
    try {
      if (typeof window === "undefined") return;
      const soundPref = localStorage.getItem("sound_effects");
      const isSoundOn = soundPref === null ? true : soundPref === "true" || soundPref === "1";
      if (isSoundOn) {
        const soundCue = localStorage.getItem("sound_cue") || "chime";
        const soundVolume = Number(localStorage.getItem("sound_volume") || 80);
        const customUrl = localStorage.getItem("custom_sound_url") || undefined;
        playAudioCue(soundCue, soundVolume, customUrl);
      }
    } catch (err) {
      console.warn("Audio chime playback skipped:", err);
    }
  };

  // Single video analysis runner
  const startSingleAnalysis = async (
    token: string,
    file: File,
    activity: string,
    surfaceType: string,
    footwear: string,
    rpe: number,
    sleepQuality: number
  ) => {
    setIsAnalyzingSingle(true);
    setSingleProgress(5);
    setSingleStage("Initializing video upload & buffer allocation...");
    setSingleFileName(file.name);
    setSingleError(null);
    setSingleResult(null);

    // Smooth realistic percentage progression
    if (singleTimerRef.current) clearInterval(singleTimerRef.current);
    singleTimerRef.current = setInterval(() => {
      setSingleProgress((prev) => {
        if (prev < 20) {
          setSingleStage("Uploading video stream to processing gateway...");
          return prev + 3;
        } else if (prev < 45) {
          setSingleStage("Extracting video frames & athlete spatial tracking...");
          return prev + 2;
        } else if (prev < 72) {
          setSingleStage("Extracting 17 YOLOv8 pose keypoints & temporal trajectory...");
          return prev + 1.5;
        } else if (prev < 88) {
          setSingleStage("Calculating dynamic knee valgus, trunk lean & deceleration G...");
          return prev + 1;
        } else if (prev < 95) {
          setSingleStage("Aggregating multi-factorial injury risks & coach prescriptions...");
          return prev + 0.5;
        }
        return prev;
      });
    }, 400);

    try {
      const targetActivity = activity.startsWith("Auto-Detect") ? "Auto-Detect" : activity;
      const res = await uploadVideo(token, file, targetActivity, surfaceType, footwear, rpe, sleepQuality);

      if (singleTimerRef.current) clearInterval(singleTimerRef.current);
      setSingleProgress(100);
      setSingleStage("Analysis Complete!");
      setSingleResult(res);

      // Play completion chime
      triggerAudioChime();

      // Trigger Top Completion Pop-Up Notification with hyperlink
      setActiveNotification({
        id: `single-${Date.now()}`,
        type: "single",
        title: "Video Analysis Complete!",
        message: `Biomechanical analysis for "${file.name}" is finished. Activity: ${res?.analytics?.activity_analyzed || "Detected"}.`,
        link: "/dashboard/upload",
        linkText: "Click here to view your single video analysis results →",
        timestamp: Date.now()
      });

      return res;
    } catch (err: any) {
      if (singleTimerRef.current) clearInterval(singleTimerRef.current);
      const msg = err instanceof Error ? err.message : "Error analyzing video";
      setSingleError(msg);
      throw err;
    } finally {
      setIsAnalyzingSingle(false);
    }
  };

  const clearSingleResult = () => {
    setSingleResult(null);
    setSingleProgress(0);
    setSingleStage("");
    setSingleFileName("");
    setSingleError(null);
  };

  const resetSingleError = () => {
    setSingleError(null);
  };

  // Dual video comparison runner (Upload dual videos)
  const startDualUploadCompare = async (
    token: string,
    formData: FormData,
    fileAName: string,
    fileBName: string
  ) => {
    setIsComparingDual(true);
    setDualProgress(5);
    setDualStage("Uploading dual trial videos to comparison engine...");
    setDualFileAName(fileAName);
    setDualFileBName(fileBName);
    setDualError(null);
    setDualResult(null);

    if (dualTimerRef.current) clearInterval(dualTimerRef.current);
    dualTimerRef.current = setInterval(() => {
      setDualProgress((prev) => {
        if (prev < 22) {
          setDualStage("Uploading Video 1 & Video 2 raw streams...");
          return prev + 2.5;
        } else if (prev < 48) {
          setDualStage("Extracting synchronized frames & athlete tracking...");
          return prev + 1.8;
        } else if (prev < 75) {
          setDualStage("Generating dual 17-keypoint skeletal pose chains...");
          return prev + 1.2;
        } else if (prev < 90) {
          setDualStage("Calculating kinematic deltas, valgus shift & flight clearance...");
          return prev + 0.8;
        } else if (prev < 96) {
          setDualStage("Synthesizing comparative coaching verdict & progression matrix...");
          return prev + 0.4;
        }
        return prev;
      });
    }, 450);

    try {
      const res = await compareVideos(token, formData);

      if (dualTimerRef.current) clearInterval(dualTimerRef.current);
      setDualProgress(100);
      setDualStage("Comparison Complete!");
      setDualResult(res);

      triggerAudioChime();

      setActiveNotification({
        id: `dual-${Date.now()}`,
        type: "dual",
        title: "Dual Video Comparison Complete!",
        message: `Comparative analysis between "${fileAName}" and "${fileBName}" has finished.`,
        link: "/dashboard/compare",
        linkText: "Click here to view your trial comparison results →",
        timestamp: Date.now()
      });

      return res;
    } catch (err: any) {
      if (dualTimerRef.current) clearInterval(dualTimerRef.current);
      const msg = err instanceof Error ? err.message : "Error comparing videos";
      setDualError(msg);
      throw err;
    } finally {
      setIsComparingDual(false);
    }
  };

  // Dual video comparison runner (History comparison)
  const startDualExistingCompare = async (
    token: string,
    idA: number,
    idB: number,
    nameA: string,
    nameB: string
  ) => {
    setIsComparingDual(true);
    setDualProgress(10);
    setDualStage("Loading historical kinematic datasets from vault...");
    setDualFileAName(nameA);
    setDualFileBName(nameB);
    setDualError(null);
    setDualResult(null);

    if (dualTimerRef.current) clearInterval(dualTimerRef.current);
    dualTimerRef.current = setInterval(() => {
      setDualProgress((prev) => {
        if (prev < 50) {
          setDualStage("Cross-referencing joint angle time-series & valgus metrics...");
          return prev + 6;
        } else if (prev < 85) {
          setDualStage("Computing progression, regression & bilateral symmetry deltas...");
          return prev + 4;
        } else if (prev < 95) {
          setDualStage("Synthesizing targeted clinical coaching verdict...");
          return prev + 1.5;
        }
        return prev;
      });
    }, 250);

    try {
      const res = await compareExistingAnalyses(token, idA, idB);

      if (dualTimerRef.current) clearInterval(dualTimerRef.current);
      setDualProgress(100);
      setDualStage("Comparison Complete!");
      setDualResult(res);

      triggerAudioChime();

      setActiveNotification({
        id: `dual-hist-${Date.now()}`,
        type: "dual",
        title: "Trial Comparison Complete!",
        message: `Comparison report between Trial #${idA} and Trial #${idB} is ready.`,
        link: "/dashboard/compare",
        linkText: "Click here to view your trial comparison results →",
        timestamp: Date.now()
      });

      return res;
    } catch (err: any) {
      if (dualTimerRef.current) clearInterval(dualTimerRef.current);
      const msg = err instanceof Error ? err.message : "Error comparing historical analyses";
      setDualError(msg);
      throw err;
    } finally {
      setIsComparingDual(false);
    }
  };

  const clearDualResult = () => {
    setDualResult(null);
    setDualProgress(0);
    setDualStage("");
    setDualFileAName("");
    setDualFileBName("");
    setDualError(null);
  };

  const resetDualError = () => {
    setDualError(null);
  };

  const dismissNotification = () => {
    setActiveNotification(null);
  };

  return (
    <AnalysisContext.Provider
      value={{
        isAnalyzingSingle,
        singleProgress,
        singleStage,
        singleFileName,
        singleResult,
        singleError,
        startSingleAnalysis,
        clearSingleResult,
        resetSingleError,

        isComparingDual,
        dualProgress,
        dualStage,
        dualFileAName,
        dualFileBName,
        dualResult,
        dualError,
        startDualUploadCompare,
        startDualExistingCompare,
        clearDualResult,
        resetDualError,

        showProgressBadge,
        setShowProgressBadge,
        activeNotification,
        dismissNotification
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return context;
};

