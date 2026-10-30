/**
 * Biomechanical Video Processing Audio Cue Engine
 * High-fidelity Web Audio API tone synthesis and custom audio playback.
 */

export interface SoundCueOption {
  id: string;
  name: string;
  description: string;
  category: "predefined" | "custom";
  icon: string;
}

export const PREDEFINED_SOUNDS: SoundCueOption[] = [
  {
    id: "chime",
    name: "Subtle Chime",
    description: "Harmonious two-tone chime (Default)",
    category: "predefined",
    icon: "🔔",
  },
  {
    id: "crystal",
    name: "Crystal Bell",
    description: "Crisp high-frequency bell with pure decay",
    category: "predefined",
    icon: "✨",
  },
  {
    id: "pulse",
    name: "Success Pulse",
    description: "Uplifting 3-step ascending chord",
    category: "predefined",
    icon: "🚀",
  },
  {
    id: "zen",
    name: "Zen Resonance",
    description: "Warm, deep acoustic gong resonance",
    category: "predefined",
    icon: "🧘",
  },
  {
    id: "synth",
    name: "Cyber Scan",
    description: "Futuristic telemetry completion sweep",
    category: "predefined",
    icon: "⚡",
  },
  {
    id: "whistle",
    name: "Athletic Whistle",
    description: "Crisp referee double-chirp trill",
    category: "predefined",
    icon: "🏆",
  },
];

let globalAudioCtx: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  if (typeof window === "undefined") return null;
  try {
    const AudioCtx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!globalAudioCtx || globalAudioCtx.state === "closed") {
      globalAudioCtx = new AudioCtx();
    }
    if (globalAudioCtx.state === "suspended") {
      globalAudioCtx.resume();
    }
    return globalAudioCtx;
  } catch (e) {
    console.warn("Web Audio API not supported:", e);
    return null;
  }
}

/**
 * Play an audio cue (predefined synthesized tone or custom audio URL)
 * @param cueId Identifier: 'chime' | 'crystal' | 'pulse' | 'zen' | 'synth' | 'whistle' | 'custom'
 * @param volume Scale 0 to 1 (or 0 to 100)
 * @param customAudioUrl Optional custom URL for uploaded audio
 */
export const playAudioCue = (
  cueId: string = "chime",
  volume: number = 80,
  customAudioUrl?: string
) => {
  if (typeof window === "undefined") return;

  // Normalize volume to 0.0 - 1.0 range
  const normalizedVolume = Math.max(0.01, Math.min(1.0, volume > 1 ? volume / 100 : volume));

  // If custom audio was chosen and a valid URL is provided
  if (cueId === "custom" && customAudioUrl) {
    try {
      const fullUrl = customAudioUrl.startsWith("http")
        ? customAudioUrl
        : `${typeof window !== "undefined" && window.location.hostname === "localhost" ? "http://localhost:8000" : "http://127.0.0.1:8000"}${customAudioUrl}`;
      const audio = new Audio(fullUrl);
      audio.volume = normalizedVolume;
      audio.play().catch((err) => {
        console.warn("Custom audio playback failed, falling back to subtle chime:", err);
        playAudioCue("chime", volume);
      });
      return;
    } catch {
      // Fallback to synthesized chime below
    }
  }

  const ctx = getAudioContext();
  if (!ctx) return;

  const now = ctx.currentTime;
  const masterGain = ctx.createGain();
  masterGain.gain.setValueAtTime(normalizedVolume * 0.35, now);
  masterGain.connect(ctx.destination);

  switch (cueId) {
    case "crystal": {
      // Crystal Bell: Pure harmonic frequencies (E6 1318.5Hz + overtone 2637Hz)
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      const gain2 = ctx.createGain();

      osc1.type = "sine";
      osc1.frequency.setValueAtTime(1318.5, now);
      gain1.gain.setValueAtTime(0.8, now);
      gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.6);

      osc2.type = "sine";
      osc2.frequency.setValueAtTime(2637, now);
      gain2.gain.setValueAtTime(0.35, now);
      gain2.gain.exponentialRampToValueAtTime(0.0001, now + 0.4);

      osc1.connect(gain1);
      osc2.connect(gain2);
      gain1.connect(masterGain);
      gain2.connect(masterGain);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 0.65);
      osc2.stop(now + 0.65);
      break;
    }

    case "pulse": {
      // Success Pulse: Fast 3-tone arpeggio (C5 -> E5 -> G5)
      const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
      notes.forEach((freq, idx) => {
        const start = now + idx * 0.08;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, start);

        gain.gain.setValueAtTime(0.6, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.28);

        osc.connect(gain);
        gain.connect(masterGain);

        osc.start(start);
        osc.stop(start + 0.3);
      });
      break;
    }

    case "zen": {
      // Zen Resonance: Deep gong / singing bowl (174Hz fundamental + 348Hz overtone)
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.type = "sine";
      osc1.frequency.setValueAtTime(174.61, now); // F3
      osc2.type = "sine";
      osc2.frequency.setValueAtTime(349.23, now); // F4

      gain.gain.setValueAtTime(0.9, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(masterGain);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 1.25);
      osc2.stop(now + 1.25);
      break;
    }

    case "synth": {
      // Cyber Scan: Rapid futuristic filter sweep
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(1760, now + 0.18);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.35);

      gain.gain.setValueAtTime(0.35, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.38);

      osc.connect(gain);
      gain.connect(masterGain);

      osc.start(now);
      osc.stop(now + 0.4);
      break;
    }

    case "whistle": {
      // Sports Whistle: Dual high frequencies with rapid vibrato
      [0, 0.12].forEach((offset) => {
        const start = now + offset;
        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const gain = ctx.createGain();

        osc1.type = "sine";
        osc1.frequency.setValueAtTime(2600, start);
        osc2.type = "triangle";
        osc2.frequency.setValueAtTime(2780, start);

        gain.gain.setValueAtTime(0.5, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.09);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(masterGain);

        osc1.start(start);
        osc2.start(start);
        osc1.stop(start + 0.1);
        osc2.stop(start + 0.1);
      });
      break;
    }

    case "chime":
    default: {
      // Subtle Chime: D5 to A5 gentle acoustic rising chime
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(587.33, now); // D5
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.14); // A5

      gain.gain.setValueAtTime(0.6, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

      osc.connect(gain);
      gain.connect(masterGain);

      osc.start(now);
      osc.stop(now + 0.45);
      break;
    }
  }
};

