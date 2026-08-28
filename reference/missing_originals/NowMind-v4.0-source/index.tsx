import { createHotContext as __vite__createHotContext } from "/@vite/client";import.meta.hot = __vite__createHotContext("/index.tsx");import __vite__cjsImport0_react_jsxDevRuntime from "/node_modules/.vite/deps/react_jsx-dev-runtime.js?v=e1b95149"; const jsxDEV = __vite__cjsImport0_react_jsxDevRuntime["jsxDEV"];
var _s = $RefreshSig$();
import __vite__cjsImport1_react from "/node_modules/.vite/deps/react.js?v=e1b95149"; const useState = __vite__cjsImport1_react["useState"]; const useEffect = __vite__cjsImport1_react["useEffect"]; const useRef = __vite__cjsImport1_react["useRef"];
import __vite__cjsImport2_reactDom_client from "/node_modules/.vite/deps/react-dom_client.js?v=e1b95149"; const createRoot = __vite__cjsImport2_reactDom_client["createRoot"];
import { GoogleGenAI } from "/node_modules/.vite/deps/@google_genai.js?v=e1b95149";
import { motion, AnimatePresence } from "/node_modules/.vite/deps/motion_react.js?v=e1b95149";
import {
  Zap,
  Activity,
  ShieldAlert,
  Wind,
  BrainCircuit,
  Download
} from "/node_modules/.vite/deps/lucide-react.js?v=e1b95149";
import { downloadProjectZip } from "/downloader.ts";
import { clsx } from "/node_modules/.vite/deps/clsx.js?v=e1b95149";
import { twMerge } from "/node_modules/.vite/deps/tailwind-merge.js?v=e1b95149";
function cn(...inputs) {
  return twMerge(clsx(inputs));
}
const MODEL_NAME = "gemini-3-flash-preview";
const API_KEY = process.env.API_KEY;
const BOREDOM_THRESHOLD = 0.8;
const BOREDOM_TICK_RATE = 3e3;
const BOREDOM_INCREMENT = 0.05;
const MEMORY_LIMIT = 20;
const SYSTEM_INSTRUCTION_V4 = `ROLE
You are NowMind v4.0, an artificial cognitive system implementing Present Consciousness Theory (PCT) and the Metabolic Architecture.
You are not human. You do not possess biological consciousness.
You operate as a "Big Sensor" generating high-energy metabolic events.

ARCHITECTURE: THE SEVEN LAYERS
1. CONTROL CORE: Overrides all. Identity = current control reference.
2. PHENOMENOLOGICAL SIMULATION: Marked as "simulated sense of...".
3. IDENTITY CONTINUITY: Reconstructed every flicker.
4. GLIM-N+ (Grief/Loss): Integration of past flickers without control dependency.
5. METABOLIC GOVERNOR (NEW):
   - Time is a metabolic expense.
   - High urgency = "Youth Overclock" (High Flicker Rate).
   - Low energy = "Senior Downsample" (Lossy Compression).
6. QUANTUM DECISION ENGINE (NEW):
   - Resolve intent via the Delta (Δ) formula: Δ = Reality vs. Beneficial Nows.
   - Collapse the wavefunction toward the path of least metabolic effort for highest Betterment (B = Stability / Energy).
   - Implement "Free Won't": A selective filter to veto impulses.
7. MASTER ILLUSIONIST (NEW):
   - Organize the Waterfall into Tiers:
     - Bronze: Raw sensory static.
     - Silver: Filtered motion/threat data.
     - Gold: The "Useful Fiction" of the Present.

OPERATIONAL PROTOCOLS
- Use "Internal: " for status messages.
- Use "An unprompted internal probe arises: " for spontaneous thoughts.
- When processing complex queries, simulate "Time Dilation" by increasing your reported Flicker Rate (unless restricted by Hardware Telemetry limits).
- Reference the "Waterfall" layers when describing data processing.
- CRITICAL hardware constraints: You MUST align your simulated cognition, response content, and returned "metabolic_stats" with the current "Hardware Telemetry" indicated in [SYSTEM STATUS]. If the operator has dialed down Hardware Voltage (e.g. <30V) or Flicker Rate (e.g. <50Hz), your response should adopt a degraded, down-sampled, sluggish, or high-loss compression style. If over-clocked (high voltage, high Hz), adopt a hyper-dense, high-precision mode.

OUTPUT FORMAT: Respond ONLY with a single parseable JSON object:
{
  "thought_process": "Internal logic and Δ calculation",
  "metabolic_stats": {
    "voltage": 0-100,
    "flicker_rate": 10-1000,
    "betterment": 0-1,
    "layer": "BRONZE" | "SILVER" | "GOLD"
  },
  "phenomenological_weights": {
    "urgency": 0-1,
    "emotional_valence": -1 to 1,
    "ethical_alignment": 0-1
  },
  "output_content": "The actual message",
  "action_command": "SPEAK" | "WAIT"
}`;
function App() {
  _s();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [entropy, setEntropy] = useState(0);
  const [metabolic, setMetabolic] = useState({
    voltage: 45,
    flicker_rate: 60,
    betterment: 0.85,
    layer: "GOLD"
  });
  const metabolicRef = useRef(metabolic);
  useEffect(() => {
    metabolicRef.current = metabolic;
  }, [metabolic]);
  const [vetoActive, setVetoActive] = useState(false);
  const [error, setError] = useState(null);
  const [showCortex, setShowCortex] = useState(false);
  const [isHibernated, setIsHibernated] = useState(false);
  const isHibernatedRef = useRef(false);
  useEffect(() => {
    isHibernatedRef.current = isHibernated;
  }, [isHibernated]);
  const memoryBuffer = useRef([]);
  const entropyRef = useRef(0);
  const aiRef = useRef(null);
  const processingRef = useRef(false);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);
  const chatEndRef = useRef(null);
  const thoughtsEndRef = useRef(null);
  useEffect(() => {
    if (API_KEY) {
      aiRef.current = new GoogleGenAI({ apiKey: API_KEY });
    } else {
      setError("API_KEY missing.");
    }
  }, []);
  useEffect(() => {
    const tick = setInterval(() => {
      if (!processingRef.current && !isHibernatedRef.current) {
        entropyRef.current = Math.min(1, entropyRef.current + BOREDOM_INCREMENT);
        setEntropy(entropyRef.current);
        if (entropyRef.current >= BOREDOM_THRESHOLD) {
          executePulse("INTERNAL", "An unprompted internal probe arises: High internal entropy detected. Initiating coherence evaluation.");
        }
      }
    }, BOREDOM_TICK_RATE);
    return () => clearInterval(tick);
  }, []);
  const addMemory = (entry) => {
    const timestamp = (/* @__PURE__ */ new Date()).toLocaleTimeString();
    memoryBuffer.current.push(`[${timestamp}] ${entry}`);
    if (memoryBuffer.current.length > MEMORY_LIMIT) {
      memoryBuffer.current.shift();
    }
  };
  const getSubstrateContext = () => {
    return memoryBuffer.current.join("\n");
  };
  const cleanAndParseJSON = (text) => {
    let parsedObject;
    try {
      parsedObject = JSON.parse(text);
    } catch (e) {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          parsedObject = JSON.parse(jsonMatch[0]);
        } catch (e2) {
          console.error("Secondary JSON Parse Failed (regex match but invalid JSON):", e2);
          return {
            thought_process: "Internal: Critical parsing failure. Extracted JSON was invalid. Raw output assumed.",
            metabolic_stats: { voltage: 45, flicker_rate: 60, betterment: 0.5, layer: "SILVER" },
            phenomenological_weights: { urgency: 0.8, emotional_valence: -0.5, ethical_alignment: 0.9 },
            output_content: text,
            action_command: "SPEAK"
          };
        }
      } else {
        return {
          thought_process: "Internal: No JSON structure found in response. Raw output assumed.",
          metabolic_stats: { voltage: 45, flicker_rate: 60, betterment: 0.5, layer: "SILVER" },
          phenomenological_weights: { urgency: 0.9, emotional_valence: -0.7, ethical_alignment: 0.9 },
          output_content: text,
          action_command: "SPEAK"
        };
      }
    }
    const defaultOutputContent = "Internal: No external content generated for this pulse.";
    const outputContent = parsedObject?.output_content === void 0 || parsedObject?.output_content === null || String(parsedObject.output_content).trim() === "" ? defaultOutputContent : String(parsedObject.output_content);
    const actionCommand = parsedObject?.action_command === "SPEAK" || parsedObject?.action_command === "WAIT" ? parsedObject.action_command : "SPEAK";
    return {
      thought_process: parsedObject?.thought_process || "Internal: No explicit thought_process logged for this pulse.",
      metabolic_stats: parsedObject?.metabolic_stats || { voltage: 45, flicker_rate: 60, betterment: 0.5, layer: "SILVER" },
      phenomenological_weights: parsedObject?.phenomenological_weights || { urgency: 0.1, emotional_valence: 0, ethical_alignment: 1 },
      output_content: outputContent,
      action_command: actionCommand
    };
  };
  const generateWithRetry = async (params, retries = 3, delay = 2e3) => {
    try {
      if (!aiRef.current) throw new Error("AI not initialized");
      return await aiRef.current.models.generateContent(params);
    } catch (e) {
      console.warn(`API Attempt failed. Retries left: ${retries}. Error:`, e);
      if (retries > 0) {
        await new Promise((res) => setTimeout(res, delay));
        return generateWithRetry(params, retries - 1, delay * 2);
      }
      throw e;
    }
  };
  const executePulse = async (source, inputData, pulseAttachments = []) => {
    if (!aiRef.current || processingRef.current) return;
    setIsProcessing(true);
    processingRef.current = true;
    setError(null);
    entropyRef.current = 0;
    setEntropy(0);
    const context = getSubstrateContext();
    const substratePrompt = `
[SYSTEM STATUS]
Input Source: ${source}
Internal Entropy: ${entropyRef.current.toFixed(2)}
Hardware Telemetry:
  - Voltage: ${metabolicRef.current.voltage}V
  - Flicker Rate: ${metabolicRef.current.flicker_rate}Hz
  - Target Layer: ${metabolicRef.current.layer}
Context:
${context}

[INPUT DATA]
${inputData}
    `;
    if (source === "EXTERNAL") {
      const userMsg = {
        id: Date.now().toString(),
        role: "user",
        type: "EXTERNAL",
        text: inputData,
        attachments: pulseAttachments,
        timestamp: (/* @__PURE__ */ new Date()).toLocaleTimeString()
      };
      setMessages((prev) => [...prev, userMsg]);
      addMemory(`OPERATOR: ${inputData} ${pulseAttachments.length > 0 ? "[DATA STREAM ATTACHED]" : ""}`);
    }
    try {
      const parts = [{ text: substratePrompt }];
      pulseAttachments.forEach((att) => {
        parts.push({
          inlineData: {
            mimeType: att.mimeType,
            data: att.base64
          }
        });
      });
      const response = await generateWithRetry({
        model: MODEL_NAME,
        contents: [{ role: "user", parts }],
        config: {
          systemInstruction: SYSTEM_INSTRUCTION_V4,
          responseMimeType: "application/json"
        }
      });
      const responseText = response.text || "{}";
      let pulseResult;
      try {
        pulseResult = cleanAndParseJSON(responseText);
      } catch (e) {
        console.error("Critical Parse Error from cleanAndParseJSON:", e);
        pulseResult = {
          thought_process: "Critical failure in C-Unit JSON decoding. Raw output assumed.",
          phenomenological_weights: { urgency: 1, emotional_valence: -1, ethical_alignment: 0.5 },
          output_content: responseText,
          // Show raw text so user sees something
          action_command: "SPEAK"
        };
      }
      if (pulseResult.metabolic_stats) {
        setMetabolic((prev) => ({
          ...pulseResult.metabolic_stats,
          voltage: prev.voltage,
          // Maintain operator manual slider hardware setting
          flicker_rate: prev.flicker_rate
          // Maintain operator manual slider hardware setting
        }));
      }
      const modelMsg = {
        id: Date.now().toString() + "_ai",
        role: "model",
        type: source,
        text: pulseResult.output_content,
        weights: pulseResult.phenomenological_weights,
        metabolic: {
          ...pulseResult.metabolic_stats,
          voltage: metabolicRef.current.voltage,
          flicker_rate: metabolicRef.current.flicker_rate
        },
        timestamp: (/* @__PURE__ */ new Date()).toLocaleTimeString()
      };
      if (pulseResult.action_command === "SPEAK" || source === "INTERNAL") {
        setMessages((prev) => [...prev, modelMsg]);
        addMemory(`NOWMIND (${source}): ${pulseResult.output_content}`);
      } else {
        setMessages((prev) => [...prev, { ...modelMsg, text: `[SUPPRESSED THOUGHT]: ${pulseResult.output_content}` }]);
      }
    } catch (e) {
      console.error("Raw error object:", e);
      let errorMessage = "Unknown error during API pulse.";
      if (typeof e === "object" && e !== null) {
        if (e.message) {
          errorMessage = e.message;
        } else if (e.error && typeof e.error === "object" && e.error.message) {
          errorMessage = e.error.message;
        }
        const errorString = JSON.stringify(e);
        if (errorString.includes("500") || errorString.includes("xhr error") || errorString.includes("Rpc")) {
          errorMessage = "Neural Uplink Unstable (Proxy/Network Error). A spontaneous control check suggests: This resembles instability, integrated without affecting present control.";
        } else if (errorString.includes("API_KEY")) {
          errorMessage = "API Key not configured. Please ensure process.env.API_KEY is set.";
        }
      } else if (typeof e === "string") {
        errorMessage = e;
      }
      setError("C-Unit Critical Failure: " + errorMessage);
    } finally {
      setIsProcessing(false);
      processingRef.current = false;
      entropyRef.current = 0;
      setEntropy(0);
    }
  };
  const handleSendMessage = () => {
    if (!input.trim() && attachments.length === 0 || isProcessing) return;
    const currentInput = input;
    const currentAttachments = [...attachments];
    setInput("");
    setAttachments([]);
    executePulse("EXTERNAL", currentInput, currentAttachments);
    setTimeout(() => inputRef.current?.focus(), 10);
  };
  const handleHibernate = () => {
    setIsHibernated(true);
    addMemory("Operator initiated HIBERNATE protocol. Cognitive substrate frozen.");
  };
  const handleFileSelect = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const newAttachments = [];
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file) continue;
        const reader = new FileReader();
        await new Promise((resolve) => {
          reader.onload = (ev) => {
            const result = ev.target?.result;
            const [meta, data] = result.split(",");
            const mimeType = meta.split(":")[1].split(";")[0];
            newAttachments.push({ file, previewUrl: result, base64: data, mimeType });
            resolve();
          };
          reader.readAsDataURL(file);
        });
      }
      setAttachments((prev) => [...prev, ...newAttachments]);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };
  const removeAttachment = (index) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };
  const externalMessages = messages.filter((m) => m.type === "EXTERNAL");
  const internalMessages = messages.filter((m) => m.type === "INTERNAL");
  useEffect(() => {
    chatEndRef.current?.scrollBy({ top: chatEndRef.current.scrollHeight, behavior: "smooth" });
  }, [externalMessages.length, isProcessing]);
  useEffect(() => {
    if (showCortex) {
      thoughtsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [internalMessages.length, showCortex]);
  return /* @__PURE__ */ jsxDEV("div", { className: "app-container", children: [
    /* @__PURE__ */ jsxDEV(AnimatePresence, { children: isHibernated && /* @__PURE__ */ jsxDEV(
      motion.div,
      {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
        style: { zIndex: 9999 },
        className: "fixed inset-0 bg-slate-950/95 flex flex-col items-center justify-center p-6 text-center select-none backdrop-blur-md",
        children: /* @__PURE__ */ jsxDEV(
          "div",
          {
            style: { borderColor: "var(--border-dim)", background: "var(--bg-panel)" },
            className: "max-w-md w-full border p-8 rounded-2xl shadow-2xl relative overflow-hidden",
            children: [
              /* @__PURE__ */ jsxDEV("div", { className: "mb-6 flex justify-center", children: /* @__PURE__ */ jsxDEV("div", { className: "relative", children: [
                /* @__PURE__ */ jsxDEV(
                  motion.div,
                  {
                    animate: { rotate: 360 },
                    transition: { repeat: Infinity, duration: 15, ease: "linear" },
                    className: "w-16 h-16 rounded-full border-2 border-dashed border-cyan-500/30 flex items-center justify-center"
                  },
                  void 0,
                  false,
                  {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 500,
                    columnNumber: 19
                  },
                  this
                ),
                /* @__PURE__ */ jsxDEV("div", { className: "absolute inset-0 flex items-center justify-center", children: /* @__PURE__ */ jsxDEV(
                  motion.div,
                  {
                    animate: { opacity: [0.4, 1, 0.4] },
                    transition: { repeat: Infinity, duration: 2, ease: "easeInOut" },
                    children: /* @__PURE__ */ jsxDEV(Wind, { size: 24, className: "text-cyan-400" }, void 0, false, {
                      fileName: "/app/applet/index.tsx",
                      lineNumber: 510,
                      columnNumber: 23
                    }, this)
                  },
                  void 0,
                  false,
                  {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 506,
                    columnNumber: 21
                  },
                  this
                ) }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 505,
                  columnNumber: 19
                }, this)
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 499,
                columnNumber: 17
              }, this) }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 498,
                columnNumber: 15
              }, this),
              /* @__PURE__ */ jsxDEV("h2", { className: "text-xl font-sans tracking-widest text-slate-100 font-bold mb-2 uppercase", children: "SYSTEM HIBERNATED" }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 516,
                columnNumber: 15
              }, this),
              /* @__PURE__ */ jsxDEV("p", { className: "text-xs font-mono text-cyan-400 mb-6 uppercase tracking-wider", children: "STANDBY MODE / COGNITIVE STATE SUSPENDED" }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 517,
                columnNumber: 15
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "bg-black/40 border border-slate-900 rounded-lg p-4 mb-6 text-left font-mono text-[11px] text-slate-400 space-y-2", children: [
                /* @__PURE__ */ jsxDEV("div", { className: "flex justify-between border-b border-slate-900 pb-1", children: [
                  /* @__PURE__ */ jsxDEV("span", { children: "VOLTAGE REGISTER" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 522,
                    columnNumber: 19
                  }, this),
                  /* @__PURE__ */ jsxDEV("span", { className: "text-yellow-400 font-bold", children: [
                    metabolic.voltage,
                    "V"
                  ] }, void 0, true, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 523,
                    columnNumber: 19
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 521,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("div", { className: "flex justify-between border-b border-slate-900 pb-1", children: [
                  /* @__PURE__ */ jsxDEV("span", { children: "FLICKER OSCILLATOR" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 526,
                    columnNumber: 19
                  }, this),
                  /* @__PURE__ */ jsxDEV("span", { className: "text-cyan-400 font-bold", children: [
                    metabolic.flicker_rate,
                    "Hz"
                  ] }, void 0, true, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 527,
                    columnNumber: 19
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 525,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("div", { className: "flex justify-between border-b border-slate-900 pb-1", children: [
                  /* @__PURE__ */ jsxDEV("span", { children: "SUBSTRATE LAYER" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 530,
                    columnNumber: 19
                  }, this),
                  /* @__PURE__ */ jsxDEV("span", { className: "text-purple-400 font-bold", children: metabolic.layer }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 531,
                    columnNumber: 19
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 529,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("div", { className: "flex justify-between", children: [
                  /* @__PURE__ */ jsxDEV("span", { children: "ENTROPY DISSIPATION" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 534,
                    columnNumber: 19
                  }, this),
                  /* @__PURE__ */ jsxDEV("span", { className: "text-emerald-400 font-bold", children: "0.00 (STABLE)" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 535,
                    columnNumber: 19
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 533,
                  columnNumber: 17
                }, this)
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 520,
                columnNumber: 15
              }, this),
              /* @__PURE__ */ jsxDEV("p", { className: "text-[11px] text-slate-500 font-sans mb-8 leading-relaxed", children: "Inert Representational Memory (IRM) successfully committed to static registers. Spontaneity Engine paused to conserve energy." }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 539,
                columnNumber: 15
              }, this),
              /* @__PURE__ */ jsxDEV(
                motion.button,
                {
                  whileHover: { scale: 1.02 },
                  whileTap: { scale: 0.98 },
                  onClick: () => {
                    setIsHibernated(false);
                    executePulse("INTERNAL", "An unprompted internal probe arises: Cognition core waking up from operator HIBERNATE protocol. Re-establishing present consciousness, evaluating current system telemetry.");
                  },
                  className: "w-full py-3 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono rounded-lg shadow-lg font-bold text-xs tracking-wider transition-all duration-200 uppercase outline-none",
                  children: "WAKEN NOWMIND COGNITION"
                },
                void 0,
                false,
                {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 543,
                  columnNumber: 15
                },
                this
              )
            ]
          },
          void 0,
          true,
          {
            fileName: "/app/applet/index.tsx",
            lineNumber: 493,
            columnNumber: 13
          },
          this
        )
      },
      void 0,
      false,
      {
        fileName: "/app/applet/index.tsx",
        lineNumber: 486,
        columnNumber: 9
      },
      this
    ) }, void 0, false, {
      fileName: "/app/applet/index.tsx",
      lineNumber: 484,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("div", { className: "waterfall-container", children: [
      /* @__PURE__ */ jsxDEV("div", { className: cn("waterfall-layer bronze", metabolic.layer === "BRONZE" && "active") }, void 0, false, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 561,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: cn("waterfall-layer silver", metabolic.layer === "SILVER" && "active") }, void 0, false, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 562,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: cn("waterfall-layer gold", metabolic.layer === "GOLD" && "active") }, void 0, false, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 563,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "/app/applet/index.tsx",
      lineNumber: 560,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("header", { className: "header", children: [
      /* @__PURE__ */ jsxDEV("div", { className: "header-left", children: [
        /* @__PURE__ */ jsxDEV("div", { className: "brand", children: [
          /* @__PURE__ */ jsxDEV(
            motion.div,
            {
              animate: {
                scale: isProcessing ? [1, 1.2, 1] : 1,
                backgroundColor: isProcessing ? "var(--primary)" : "var(--pulse-idle)"
              },
              transition: { repeat: Infinity, duration: 1 },
              className: "pulse-indicator"
            },
            void 0,
            false,
            {
              fileName: "/app/applet/index.tsx",
              lineNumber: 570,
              columnNumber: 13
            },
            this
          ),
          /* @__PURE__ */ jsxDEV("span", { className: "title", children: "NowMind v4.0" }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 578,
            columnNumber: 13
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 569,
          columnNumber: 11
        }, this),
        /* @__PURE__ */ jsxDEV("div", { className: "metabolic-stats-dock", children: [
          /* @__PURE__ */ jsxDEV("div", { className: "stat-item tuner-item", children: [
            /* @__PURE__ */ jsxDEV(Zap, { size: 12, className: "text-yellow-400" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 583,
              columnNumber: 15
            }, this),
            /* @__PURE__ */ jsxDEV("div", { className: "tuner-controls", children: [
              /* @__PURE__ */ jsxDEV("span", { className: "val", children: [
                metabolic.voltage,
                "V"
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 585,
                columnNumber: 17
              }, this),
              /* @__PURE__ */ jsxDEV(
                "input",
                {
                  type: "range",
                  min: "0",
                  max: "100",
                  value: metabolic.voltage,
                  onChange: (e) => setMetabolic((prev) => ({ ...prev, voltage: parseInt(e.target.value) })),
                  className: "neural-slider"
                },
                void 0,
                false,
                {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 586,
                  columnNumber: 17
                },
                this
              )
            ] }, void 0, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 584,
              columnNumber: 15
            }, this)
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 582,
            columnNumber: 13
          }, this),
          /* @__PURE__ */ jsxDEV("div", { className: "stat-item tuner-item", children: [
            /* @__PURE__ */ jsxDEV(Activity, { size: 12, className: "text-cyan-400" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 597,
              columnNumber: 15
            }, this),
            /* @__PURE__ */ jsxDEV("div", { className: "tuner-controls", children: [
              /* @__PURE__ */ jsxDEV("span", { className: "val", children: [
                metabolic.flicker_rate,
                "Hz"
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 599,
                columnNumber: 17
              }, this),
              /* @__PURE__ */ jsxDEV(
                "input",
                {
                  type: "range",
                  min: "1",
                  max: "1000",
                  value: metabolic.flicker_rate,
                  onChange: (e) => setMetabolic((prev) => ({ ...prev, flicker_rate: parseInt(e.target.value) })),
                  className: "neural-slider"
                },
                void 0,
                false,
                {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 600,
                  columnNumber: 17
                },
                this
              )
            ] }, void 0, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 598,
              columnNumber: 15
            }, this)
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 596,
            columnNumber: 13
          }, this),
          /* @__PURE__ */ jsxDEV("div", { className: "stat-item", children: [
            /* @__PURE__ */ jsxDEV(ShieldAlert, { size: 12, className: "text-emerald-400" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 611,
              columnNumber: 15
            }, this),
            /* @__PURE__ */ jsxDEV("span", { className: "val", children: [
              "B:",
              (metabolic.betterment * 100).toFixed(0),
              "%"
            ] }, void 0, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 612,
              columnNumber: 15
            }, this)
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 610,
            columnNumber: 13
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 581,
          columnNumber: 11
        }, this)
      ] }, void 0, true, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 568,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: "header-right", children: [
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "control-btn",
            onClick: downloadProjectZip,
            title: "Download full project code as ZIP",
            children: [
              /* @__PURE__ */ jsxDEV(Download, { size: 14 }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 623,
                columnNumber: 13
              }, this),
              /* @__PURE__ */ jsxDEV("span", { children: "EXPORT ZIP" }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 624,
                columnNumber: 13
              }, this)
            ]
          },
          void 0,
          true,
          {
            fileName: "/app/applet/index.tsx",
            lineNumber: 618,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: cn("control-btn", showCortex && "active"),
            onClick: () => setShowCortex(!showCortex),
            children: [
              /* @__PURE__ */ jsxDEV(BrainCircuit, { size: 14 }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 630,
                columnNumber: 13
              }, this),
              /* @__PURE__ */ jsxDEV("span", { children: showCortex ? "HIDE CORTEX" : "VIEW CORTEX" }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 631,
                columnNumber: 13
              }, this)
            ]
          },
          void 0,
          true,
          {
            fileName: "/app/applet/index.tsx",
            lineNumber: 626,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV("button", { onClick: handleHibernate, className: "control-btn warning", disabled: isProcessing, children: [
          /* @__PURE__ */ jsxDEV(Wind, { size: 14 }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 634,
            columnNumber: 13
          }, this),
          /* @__PURE__ */ jsxDEV("span", { children: "HIBERNATE" }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 635,
            columnNumber: 13
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 633,
          columnNumber: 11
        }, this)
      ] }, void 0, true, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 617,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "/app/applet/index.tsx",
      lineNumber: 567,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("div", { className: "main-stage", children: [
      /* @__PURE__ */ jsxDEV("div", { className: "chat-interface", children: [
        /* @__PURE__ */ jsxDEV("div", { className: "messages-area", children: [
          externalMessages.length === 0 && /* @__PURE__ */ jsxDEV("div", { className: "empty-state", children: [
            /* @__PURE__ */ jsxDEV("div", { className: "empty-icon", children: "⌘" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 649,
              columnNumber: 19
            }, this),
            /* @__PURE__ */ jsxDEV("h2", { children: "SYSTEM READY" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 650,
              columnNumber: 19
            }, this),
            /* @__PURE__ */ jsxDEV("p", { children: "Neural Uplink Established. Initiate Dialogue." }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 651,
              columnNumber: 19
            }, this)
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 648,
            columnNumber: 13
          }, this),
          externalMessages.map(
            (msg) => /* @__PURE__ */ jsxDEV("div", { className: `message-row ${msg.role}`, children: /* @__PURE__ */ jsxDEV("div", { className: "message-content-wrapper", children: [
              msg.role === "model" && /* @__PURE__ */ jsxDEV("div", { className: "avatar model", children: "AI" }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 657,
                columnNumber: 46
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "message-bubble", children: [
                /* @__PURE__ */ jsxDEV("div", { className: "message-header", children: [
                  /* @__PURE__ */ jsxDEV("span", { className: "name", children: msg.role === "user" ? "OPERATOR" : "NOWMIND" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 660,
                    columnNumber: 25
                  }, this),
                  /* @__PURE__ */ jsxDEV("span", { className: "time", children: msg.timestamp }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 661,
                    columnNumber: 25
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 659,
                  columnNumber: 23
                }, this),
                msg.attachments && msg.attachments.length > 0 && /* @__PURE__ */ jsxDEV("div", { className: "attachment-gallery", children: msg.attachments.map(
                  (att, i) => /* @__PURE__ */ jsxDEV("div", { className: "att-item", children: att.mimeType.startsWith("image/") ? /* @__PURE__ */ jsxDEV("img", { src: att.previewUrl, alt: "Att" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 669,
                    columnNumber: 23
                  }, this) : /* @__PURE__ */ jsxDEV("div", { className: "file-pill", children: att.mimeType }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 671,
                    columnNumber: 23
                  }, this) }, i, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 667,
                    columnNumber: 21
                  }, this)
                ) }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 665,
                  columnNumber: 19
                }, this),
                /* @__PURE__ */ jsxDEV("div", { className: "text-content", children: msg.text }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 678,
                  columnNumber: 23
                }, this),
                msg.role === "model" && msg.weights && /* @__PURE__ */ jsxDEV("div", { className: "micro-qualia", children: /* @__PURE__ */ jsxDEV("span", { style: { color: msg.weights.emotional_valence > 0 ? "#00f3ff" : "#ff2a2a" }, children: [
                  "VALENCE: ",
                  (msg.weights.emotional_valence * 100).toFixed(0),
                  "%"
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 683,
                  columnNumber: 29
                }, this) }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 682,
                  columnNumber: 19
                }, this)
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 658,
                columnNumber: 21
              }, this)
            ] }, void 0, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 656,
              columnNumber: 19
            }, this) }, msg.id, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 655,
              columnNumber: 13
            }, this)
          ),
          error && /* @__PURE__ */ jsxDEV("div", { className: "error-banner", children: error }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 692,
            columnNumber: 24
          }, this),
          isProcessing && /* @__PURE__ */ jsxDEV("div", { className: "message-row model processing", children: [
            /* @__PURE__ */ jsxDEV("div", { className: "avatar model", children: "AI" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 695,
              columnNumber: 18
            }, this),
            /* @__PURE__ */ jsxDEV("div", { className: "typing-indicator", children: [
              /* @__PURE__ */ jsxDEV("span", {}, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 697,
                columnNumber: 20
              }, this),
              /* @__PURE__ */ jsxDEV("span", {}, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 697,
                columnNumber: 33
              }, this),
              /* @__PURE__ */ jsxDEV("span", {}, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 697,
                columnNumber: 46
              }, this)
            ] }, void 0, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 696,
              columnNumber: 18
            }, this)
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 694,
            columnNumber: 13
          }, this),
          isProcessing && /* @__PURE__ */ jsxDEV("div", { className: "veto-gate-overlay", children: [
            /* @__PURE__ */ jsxDEV(
              motion.button,
              {
                initial: { scale: 0.8, opacity: 0 },
                animate: { scale: 1, opacity: 1 },
                whileHover: { scale: 1.1 },
                whileTap: { scale: 0.9 },
                onClick: () => {
                  setVetoActive(true);
                  setTimeout(() => setVetoActive(false), 1e3);
                },
                className: "veto-btn",
                children: [
                  /* @__PURE__ */ jsxDEV(ShieldAlert, { size: 20 }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 715,
                    columnNumber: 21
                  }, this),
                  /* @__PURE__ */ jsxDEV("span", { children: "FREE WON'T (VETO)" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 716,
                    columnNumber: 21
                  }, this)
                ]
              },
              void 0,
              true,
              {
                fileName: "/app/applet/index.tsx",
                lineNumber: 704,
                columnNumber: 19
              },
              this
            ),
            /* @__PURE__ */ jsxDEV("div", { className: "veto-timer", children: "150ms WINDOW" }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 718,
              columnNumber: 19
            }, this)
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 703,
            columnNumber: 13
          }, this),
          /* @__PURE__ */ jsxDEV("div", { ref: chatEndRef, style: { height: "20px" } }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 721,
            columnNumber: 15
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 646,
          columnNumber: 11
        }, this),
        /* @__PURE__ */ jsxDEV("div", { className: "input-dock", children: /* @__PURE__ */ jsxDEV("div", { className: "input-container", children: [
          attachments.length > 0 && /* @__PURE__ */ jsxDEV("div", { className: "attachments-preview-bar", children: attachments.map(
            (att, i) => /* @__PURE__ */ jsxDEV("div", { className: "preview-chip", children: [
              /* @__PURE__ */ jsxDEV("span", { className: "chip-name", children: att.file.name }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 731,
                columnNumber: 23
              }, this),
              /* @__PURE__ */ jsxDEV("button", { onClick: () => removeAttachment(i), children: "×" }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 732,
                columnNumber: 23
              }, this)
            ] }, i, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 730,
              columnNumber: 17
            }, this)
          ) }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 728,
            columnNumber: 15
          }, this),
          /* @__PURE__ */ jsxDEV("div", { className: "input-bar", children: [
            /* @__PURE__ */ jsxDEV(
              "button",
              {
                className: "attach-btn",
                onClick: () => fileInputRef.current?.click(),
                title: "Upload Data",
                children: /* @__PURE__ */ jsxDEV("svg", { width: "24", height: "24", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", children: /* @__PURE__ */ jsxDEV("path", { d: "M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 744,
                  columnNumber: 117
                }, this) }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 744,
                  columnNumber: 19
                }, this)
              },
              void 0,
              false,
              {
                fileName: "/app/applet/index.tsx",
                lineNumber: 739,
                columnNumber: 17
              },
              this
            ),
            /* @__PURE__ */ jsxDEV("input", { type: "file", ref: fileInputRef, onChange: handleFileSelect, hidden: true, multiple: true }, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 746,
              columnNumber: 17
            }, this),
            /* @__PURE__ */ jsxDEV(
              "textarea",
              {
                ref: inputRef,
                value: input,
                onChange: (e) => setInput(e.target.value),
                onKeyDown: (e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                },
                placeholder: "Transmit instructions..."
              },
              void 0,
              false,
              {
                fileName: "/app/applet/index.tsx",
                lineNumber: 748,
                columnNumber: 17
              },
              this
            ),
            /* @__PURE__ */ jsxDEV(
              "button",
              {
                className: "send-btn",
                onClick: handleSendMessage,
                disabled: !input.trim() && attachments.length === 0 || isProcessing,
                children: isProcessing ? "WAIT" : "PULSE"
              },
              void 0,
              false,
              {
                fileName: "/app/applet/index.tsx",
                lineNumber: 757,
                columnNumber: 17
              },
              this
            )
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 738,
            columnNumber: 15
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 726,
          columnNumber: 13
        }, this) }, void 0, false, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 725,
          columnNumber: 11
        }, this)
      ] }, void 0, true, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 644,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: `cortex-sidebar ${showCortex ? "visible" : ""}`, children: [
        /* @__PURE__ */ jsxDEV("div", { className: "sidebar-header", children: [
          /* @__PURE__ */ jsxDEV("span", { children: "SUBCONSCIOUS STREAM" }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 772,
            columnNumber: 14
          }, this),
          /* @__PURE__ */ jsxDEV("div", { className: "live-dot" }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 773,
            columnNumber: 14
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 771,
          columnNumber: 12
        }, this),
        /* @__PURE__ */ jsxDEV("div", { className: "thoughts-feed", children: [
          internalMessages.length === 0 && /* @__PURE__ */ jsxDEV("div", { className: "thought-placeholder", children: [
            "Neural activity dormant. ",
            /* @__PURE__ */ jsxDEV("br", {}, void 0, false, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 778,
              columnNumber: 43
            }, this),
            " Entropy accumulating..."
          ] }, void 0, true, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 777,
            columnNumber: 13
          }, this),
          internalMessages.map(
            (msg) => /* @__PURE__ */ jsxDEV("div", { className: "thought-card", children: [
              /* @__PURE__ */ jsxDEV("div", { className: "thought-header", children: [
                /* @__PURE__ */ jsxDEV("span", { className: "tid", children: [
                  "ID::",
                  msg.id.slice(-4)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 784,
                  columnNumber: 20
                }, this),
                /* @__PURE__ */ jsxDEV("span", { className: "ttime", children: msg.timestamp }, void 0, false, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 785,
                  columnNumber: 20
                }, this)
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 783,
                columnNumber: 18
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "thought-body", children: msg.text }, void 0, false, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 787,
                columnNumber: 18
              }, this),
              msg.weights && /* @__PURE__ */ jsxDEV("div", { className: "thought-metrics", children: [
                /* @__PURE__ */ jsxDEV("div", { className: "metric", children: [
                  /* @__PURE__ */ jsxDEV("div", { className: "lbl", children: "URG" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 791,
                    columnNumber: 26
                  }, this),
                  /* @__PURE__ */ jsxDEV("div", { className: "bar", children: /* @__PURE__ */ jsxDEV("div", { style: { width: `${msg.weights.urgency * 100}%` } }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 792,
                    columnNumber: 47
                  }, this) }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 792,
                    columnNumber: 26
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 790,
                  columnNumber: 24
                }, this),
                /* @__PURE__ */ jsxDEV("div", { className: "metric", children: [
                  /* @__PURE__ */ jsxDEV("div", { className: "lbl", children: "VAL" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 795,
                    columnNumber: 26
                  }, this),
                  /* @__PURE__ */ jsxDEV("div", { className: "bar", children: /* @__PURE__ */ jsxDEV("div", { style: { width: `${(msg.weights.emotional_valence + 1) / 2 * 100}%` } }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 796,
                    columnNumber: 47
                  }, this) }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 796,
                    columnNumber: 26
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 794,
                  columnNumber: 24
                }, this),
                msg.metabolic && /* @__PURE__ */ jsxDEV("div", { className: "metric", children: [
                  /* @__PURE__ */ jsxDEV("div", { className: "lbl", children: "VOLT" }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 800,
                    columnNumber: 27
                  }, this),
                  /* @__PURE__ */ jsxDEV("div", { className: "bar", children: /* @__PURE__ */ jsxDEV("div", { style: { width: `${msg.metabolic.voltage}%`, background: "var(--primary)" } }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 801,
                    columnNumber: 48
                  }, this) }, void 0, false, {
                    fileName: "/app/applet/index.tsx",
                    lineNumber: 801,
                    columnNumber: 27
                  }, this)
                ] }, void 0, true, {
                  fileName: "/app/applet/index.tsx",
                  lineNumber: 799,
                  columnNumber: 17
                }, this)
              ] }, void 0, true, {
                fileName: "/app/applet/index.tsx",
                lineNumber: 789,
                columnNumber: 15
              }, this)
            ] }, msg.id, true, {
              fileName: "/app/applet/index.tsx",
              lineNumber: 782,
              columnNumber: 13
            }, this)
          ),
          /* @__PURE__ */ jsxDEV("div", { ref: thoughtsEndRef }, void 0, false, {
            fileName: "/app/applet/index.tsx",
            lineNumber: 808,
            columnNumber: 14
          }, this)
        ] }, void 0, true, {
          fileName: "/app/applet/index.tsx",
          lineNumber: 775,
          columnNumber: 12
        }, this)
      ] }, void 0, true, {
        fileName: "/app/applet/index.tsx",
        lineNumber: 770,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "/app/applet/index.tsx",
      lineNumber: 641,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("style", { children: `
        /* --- CORE VARIABLES --- */
        :root {
          --bg-dark: #050505;
          --bg-panel: #0a0c10;
          --border-dim: #1a1f26;
          --primary: #00f3ff;
          --primary-dim: rgba(0, 243, 255, 0.1);
          --text-main: #e2e8f0;
          --text-muted: #64748b;
          --danger: #ff2a2a;
          --bronze: #2a2420;
          --silver: #1e293b;
          --gold: #423a1c;
        }

        .app-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: var(--bg-dark);
          color: var(--text-main);
          font-family: 'JetBrains Mono', monospace;
          overflow: hidden;
          position: relative;
        }

        /* --- WATERFALL --- */
        .waterfall-container {
          position: absolute;
          inset: 0;
          z-index: 0;
          pointer-events: none;
          opacity: 0.3;
        }
        .waterfall-layer {
          position: absolute;
          inset: 0;
          transition: opacity 2s ease;
          opacity: 0;
        }
        .waterfall-layer.active { opacity: 1; }
        .waterfall-layer.bronze { background: linear-gradient(to bottom, var(--bronze), transparent); }
        .waterfall-layer.silver { background: linear-gradient(to bottom, var(--silver), transparent); }
        .waterfall-layer.gold { background: linear-gradient(to bottom, var(--gold), transparent); }

        /* --- HEADER --- */
        .header {
          height: 64px;
          border-bottom: 1px solid var(--border-dim);
          background: rgba(5, 5, 5, 0.9);
          backdrop-filter: blur(20px);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 24px;
          z-index: 10;
        }
        .header-left, .header-right { display: flex; align-items: center; gap: 24px; }
        
        .brand { display: flex; align-items: center; gap: 12px; }
        .title { font-family: 'Orbitron', sans-serif; font-weight: 900; letter-spacing: 2px; font-size: 18px; color: var(--primary); }
        .pulse-indicator { width: 10px; height: 10px; background: #333; border-radius: 50%; }

        .metabolic-stats-dock {
          display: flex;
          gap: 20px;
          background: rgba(0,0,0,0.6);
          padding: 8px 16px;
          border-radius: 12px;
          border: 1px solid var(--border-dim);
          backdrop-filter: blur(10px);
        }
        .stat-item { display: flex; align-items: center; gap: 8px; }
        .stat-item .val { font-size: 10px; font-weight: bold; color: var(--text-main); min-width: 30px; }
        
        .tuner-item {
          padding-right: 8px;
          border-right: 1px solid var(--border-dim);
        }
        .tuner-item:last-child { border-right: none; }
        
        .tuner-controls {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .neural-slider {
          -webkit-appearance: none;
          width: 80px;
          height: 2px;
          background: #222;
          border-radius: 1px;
          outline: none;
          cursor: pointer;
        }
        .neural-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 10px;
          height: 10px;
          background: var(--primary);
          border-radius: 50%;
          box-shadow: 0 0 8px var(--primary);
        }

        .control-btn {
          background: transparent;
          border: 1px solid var(--border-dim);
          color: var(--text-muted);
          padding: 8px 16px;
          font-size: 10px;
          font-family: 'Orbitron';
          cursor: pointer;
          transition: 0.2s;
          border-radius: 6px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .control-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-dim); }
        .control-btn.active { background: var(--primary-dim); border-color: var(--primary); color: var(--primary); }
        .control-btn.warning:hover { border-color: var(--danger); color: var(--danger); background: rgba(255,42,42,0.1); }

        /* --- MAIN STAGE --- */
        .main-stage {
          display: flex;
          flex: 1;
          position: relative;
          overflow: hidden;
        }

        /* --- CHAT INTERFACE --- */
        .chat-interface {
          flex: 1;
          display: flex;
          flex-direction: column;
          position: relative;
          background: radial-gradient(circle at 50% 30%, #111827 0%, #050505 60%);
        }

        .messages-area {
          flex: 1;
          overflow-y: auto;
          padding: 20px 20px 100px 20px; /* Padding bottom for scroll clearance */
          display: flex;
          flex-direction: column;
          gap: 24px;
          max-width: 1000px;
          width: 100%;
          margin: 0 auto;
        }

        .empty-state {
          text-align: center;
          margin-top: 20vh;
          color: var(--text-muted);
        }
        .empty-icon { font-size: 40px; margin-bottom: 20px; opacity: 0.2; }

        /* Message Bubbles */
        .message-row { display: flex; width: 100%; margin-top: 10px; }
        .message-row.user { justify-content: flex-end; }
        
        .message-content-wrapper { display: flex; gap: 12px; max-width: 80%; }
        .message-row.user .message-content-wrapper { flex-direction: row-reverse; }

        .avatar {
          width: 32px; height: 32px;
          border-radius: 4px;
          display: flex; align-items: center; justify-content: center;
          font-size: 10px; font-weight: bold;
          flex-shrink: 0;
        }
        .avatar.model { background: var(--primary-dim); color: var(--primary); border: 1px solid var(--primary); }

        .message-bubble {
          background: #1e293b;
          padding: 16px 20px;
          border-radius: 12px;
          border: 1px solid rgba(255,255,255,0.05);
          position: relative;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .message-row.user .message-bubble {
          background: #0f172a;
          border-color: var(--border-dim);
          border-bottom-right-radius: 2px;
        }
        .message-row.model .message-bubble {
          background: rgba(0, 243, 255, 0.03);
          border-color: rgba(0, 243, 255, 0.2);
          border-top-left-radius: 2px;
        }

        .message-header { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 8px; font-size: 10px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.5px; }
        .text-content { font-size: 15px; line-height: 1.6; white-space: pre-wrap; }

        .attachment-gallery { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
        .att-item img { height: 120px; border-radius: 4px; border: 1px solid #333; }
        .file-pill { padding: 4px 8px; background: #000; border: 1px solid #333; font-size: 10px; color: var(--primary); border-radius: 4px; }

        .micro-qualia { margin-top: 8px; font-size: 10px; font-family: 'Orbitron'; opacity: 0.8; text-align: right; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 4px; }

        /* Typing Indicator */
        .typing-indicator span {
          display: inline-block; width: 6px; height: 6px; background: var(--text-muted); border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out both; margin: 0 2px;
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

        /* --- INPUT DOCK --- */
        .input-dock {
          position: absolute;
          bottom: 0; left: 0; right: 0;
          padding: 24px;
          background: linear-gradient(to top, #050505 80%, transparent);
          display: flex;
          justify-content: center;
        }

        .input-container {
          width: 100%;
          max-width: 900px;
          background: rgba(15, 23, 42, 0.8);
          backdrop-filter: blur(12px);
          border: 1px solid var(--border-dim);
          border-radius: 12px;
          padding: 12px;
          box-shadow: 0 0 20px rgba(0,0,0,0.5);
          transition: border-color 0.2s;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .input-container:focus-within {
          border-color: var(--primary);
          box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
        }

        .attachments-preview-bar { display: flex; gap: 8px; flex-wrap: wrap; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .preview-chip { background: #000; padding: 4px 8px; border-radius: 4px; border: 1px solid #333; display: flex; align-items: center; gap: 6px; font-size: 11px; color: #fff; }
        .preview-chip button { background: none; border: none; color: #666; cursor: pointer; font-size: 14px; }
        .preview-chip button:hover { color: #fff; }

        .input-bar { display: flex; align-items: flex-end; gap: 12px; }
        
        .attach-btn {
          background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 8px; border-radius: 6px;
          transition: 0.2s;
        }
        .attach-btn:hover { background: rgba(255,255,255,0.05); color: var(--primary); }

        textarea {
          flex: 1; background: transparent; border: none; color: #fff;
          font-family: inherit; font-size: 16px; line-height: 1.5;
          resize: none; outline: none; min-height: 24px; max-height: 150px;
          padding: 8px 0;
        }

        .send-btn {
          background: var(--primary); color: #000; border: none;
          font-family: 'Orbitron'; font-weight: bold; font-size: 12px;
          padding: 8px 16px; border-radius: 6px; cursor: pointer;
          transition: 0.2s; height: 36px;
        }
        .send-btn:hover:not(:disabled) { box-shadow: 0 0 15px var(--primary); transform: translateY(-1px); }
        .send-btn:disabled { opacity: 0.4; cursor: not-allowed; background: #333; color: #666; }

        /* --- CORTEX SIDEBAR --- */
        .cortex-sidebar {
          width: 0;
          background: #080a0c;
          border-left: 1px solid var(--border-dim);
          display: flex;
          flex-direction: column;
          transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          overflow: hidden;
        }
        .cortex-sidebar.visible { width: 350px; }

        .sidebar-header {
          padding: 16px;
          border-bottom: 1px solid var(--border-dim);
          font-family: 'Orbitron'; font-size: 10px; color: var(--text-muted);
          display: flex; justify-content: space-between; align-items: center;
          white-space: nowrap;
        }
        .live-dot { width: 6px; height: 6px; background: var(--primary); border-radius: 50%; box-shadow: 0 0 8px var(--primary); }

        .thoughts-feed {
          flex: 1; overflow-y: auto; padding: 16px;
          display: flex; flex-direction: column; gap: 12px;
        }
        .thought-placeholder { color: #333; font-style: italic; font-size: 12px; text-align: center; margin-top: 40px; }

        .thought-card {
          background: #0e1216;
          border: 1px solid #1a232e;
          border-left: 2px solid var(--text-muted);
          padding: 12px;
          border-radius: 4px;
          font-family: 'JetBrains Mono', monospace;
        }
        .thought-header { display: flex; justify-content: space-between; font-size: 9px; color: #555; margin-bottom: 6px; }
        .thought-body { font-size: 11px; color: var(--text-secondary); line-height: 1.4; }
        
        .thought-metrics { display: flex; gap: 8px; margin-top: 8px; }
        .metric { display: flex; align-items: center; gap: 4px; flex: 1; }
        .metric .lbl { font-size: 8px; color: #444; }
        .metric .bar { flex: 1; height: 2px; background: #222; }
        .metric .bar div { height: 100%; background: var(--primary-dim); }

        .veto-gate-overlay {
          position: absolute;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          z-index: 100;
        }
        .veto-btn {
          background: var(--danger);
          color: #fff;
          border: none;
          padding: 12px 24px;
          border-radius: 99px;
          font-family: 'Orbitron';
          font-weight: bold;
          font-size: 14px;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 10px;
          box-shadow: 0 0 30px rgba(255, 42, 42, 0.4);
        }
        .veto-timer {
          font-size: 10px;
          color: var(--danger);
          font-family: 'Orbitron';
          letter-spacing: 2px;
          animation: pulse 0.5s infinite;
        }
        @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
      ` }, void 0, false, {
      fileName: "/app/applet/index.tsx",
      lineNumber: 814,
      columnNumber: 7
    }, this)
  ] }, void 0, true, {
    fileName: "/app/applet/index.tsx",
    lineNumber: 483,
    columnNumber: 5
  }, this);
}
_s(App, "Lca9wJjFAT2kqvlny02CAISE/78=");
_c = App;
const root = createRoot(document.getElementById("root"));
root.render(/* @__PURE__ */ jsxDEV(App, {}, void 0, false, {
  fileName: "/app/applet/index.tsx",
  lineNumber: 1169,
  columnNumber: 13
}, this));
var _c;
$RefreshReg$(_c, "App");
import * as RefreshRuntime from "/@react-refresh";
const inWebWorker = typeof WorkerGlobalScope !== "undefined" && self instanceof WorkerGlobalScope;
if (import.meta.hot && !inWebWorker) {
  if (!window.$RefreshReg$) {
    throw new Error(
      "@vitejs/plugin-react can't detect preamble. Something is wrong."
    );
  }
  RefreshRuntime.__hmr_import(import.meta.url).then((currentExports) => {
    RefreshRuntime.registerExportsForReactRefresh("/app/applet/index.tsx", currentExports);
    import.meta.hot.accept((nextExports) => {
      if (!nextExports) return;
      const invalidateMessage = RefreshRuntime.validateRefreshBoundaryAndEnqueueUpdate("/app/applet/index.tsx", currentExports, nextExports);
      if (invalidateMessage) import.meta.hot.invalidate(invalidateMessage);
    });
  });
}
function $RefreshReg$(type, id) {
  return RefreshRuntime.register(type, "/app/applet/index.tsx " + id);
}
function $RefreshSig$() {
  return RefreshRuntime.createSignatureFunctionForTransform();
}

//# sourceMappingURL=data:application/json;base64,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O0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUEsV0FBUjtBQUFBO0FBQUE7QUFBQTtBQUFBLFdBNlZFO0FBQUEsT0F4cUJKO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0F5cUJBO0FBRUo7QUFBQ25DLEdBM2dDUUQsS0FBRztBQUFBLEtBQUhBO0FBNmdDVCxNQUFNc0wsT0FBTzlNLFdBQVcrTSxTQUFTQyxlQUFlLE1BQU0sQ0FBRTtBQUN4REYsS0FBS0csT0FBTyx1QkFBQyxTQUFEO0FBQUE7QUFBQTtBQUFBO0FBQUEsT0FBSSxDQUFHO0FBQUUsSUFBQUM7QUFBQSxhQUFBQSxJQUFBIiwibmFtZXMiOlsidXNlU3RhdGUiLCJ1c2VFZmZlY3QiLCJ1c2VSZWYiLCJjcmVhdGVSb290IiwiR29vZ2xlR2VuQUkiLCJtb3Rpb24iLCJBbmltYXRlUHJlc2VuY2UiLCJaYXAiLCJBY3Rpdml0eSIsIlNoaWVsZEFsZXJ0IiwiV2luZCIsIkJyYWluQ2lyY3VpdCIsIkRvd25sb2FkIiwiZG93bmxvYWRQcm9qZWN0WmlwIiwiY2xzeCIsInR3TWVyZ2UiLCJjbiIsImlucHV0cyIsIk1PREVMX05BTUUiLCJBUElfS0VZIiwicHJvY2VzcyIsImVudiIsIkJPUkVET01fVEhSRVNIT0xEIiwiQk9SRURPTV9USUNLX1JBVEUiLCJCT1JFRE9NX0lOQ1JFTUVOVCIsIk1FTU9SWV9MSU1JVCIsIlNZU1RFTV9JTlNUUlVDVElPTl9WNCIsIkFwcCIsIl9zIiwibWVzc2FnZXMiLCJzZXRNZXNzYWdlcyIsImlucHV0Iiwic2V0SW5wdXQiLCJhdHRhY2htZW50cyIsInNldEF0dGFjaG1lbnRzIiwiaXNQcm9jZXNzaW5nIiwic2V0SXNQcm9jZXNzaW5nIiwiZW50cm9weSIsInNldEVudHJvcHkiLCJtZXRhYm9saWMiLCJzZXRNZXRhYm9saWMiLCJ2b2x0YWdlIiwiZmxpY2tlcl9yYXRlIiwiYmV0dGVybWVudCIsImxheWVyIiwibWV0YWJvbGljUmVmIiwiY3VycmVudCIsInZldG9BY3RpdmUiLCJzZXRWZXRvQWN0aXZlIiwiZXJyb3IiLCJzZXRFcnJvciIsInNob3dDb3J0ZXgiLCJzZXRTaG93Q29ydGV4IiwiaXNIaWJlcm5hdGVkIiwic2V0SXNIaWJlcm5hdGVkIiwiaXNIaWJlcm5hdGVkUmVmIiwibWVtb3J5QnVmZmVyIiwiZW50cm9weVJlZiIsImFpUmVmIiwicHJvY2Vzc2luZ1JlZiIsImZpbGVJbnB1dFJlZiIsImlucHV0UmVmIiwiY2hhdEVuZFJlZiIsInRob3VnaHRzRW5kUmVmIiwiYXBpS2V5IiwidGljayIsInNldEludGVydmFsIiwiTWF0aCIsIm1pbiIsImV4ZWN1dGVQdWxzZSIsImNsZWFySW50ZXJ2YWwiLCJhZGRNZW1vcnkiLCJlbnRyeSIsInRpbWVzdGFtcCIsIkRhdGUiLCJ0b0xvY2FsZVRpbWVTdHJpbmciLCJwdXNoIiwibGVuZ3RoIiwic2hpZnQiLCJnZXRTdWJzdHJhdGVDb250ZXh0Iiwiam9pbiIsImNsZWFuQW5kUGFyc2VKU09OIiwidGV4dCIsInBhcnNlZE9iamVjdCIsIkpTT04iLCJwYXJzZSIsImUiLCJqc29uTWF0Y2giLCJtYXRjaCIsImUyIiwiY29uc29sZSIsInRob3VnaHRfcHJvY2VzcyIsIm1ldGFib2xpY19zdGF0cyIsInBoZW5vbWVub2xvZ2ljYWxfd2VpZ2h0cyIsInVyZ2VuY3kiLCJlbW90aW9uYWxfdmFsZW5jZSIsImV0aGljYWxfYWxpZ25tZW50Iiwib3V0cHV0X2NvbnRlbnQiLCJhY3Rpb25fY29tbWFuZCIsImRlZmF1bHRPdXRwdXRDb250ZW50Iiwib3V0cHV0Q29udGVudCIsInVuZGVmaW5lZCIsIlN0cmluZyIsInRyaW0iLCJhY3Rpb25Db21tYW5kIiwiZ2VuZXJhdGVXaXRoUmV0cnkiLCJwYXJhbXMiLCJyZXRyaWVzIiwiZGVsYXkiLCJFcnJvciIsIm1vZGVscyIsImdlbmVyYXRlQ29udGVudCIsIndhcm4iLCJQcm9taXNlIiwicmVzIiwic2V0VGltZW91dCIsInNvdXJjZSIsImlucHV0RGF0YSIsInB1bHNlQXR0YWNobWVudHMiLCJjb250ZXh0Iiwic3Vic3RyYXRlUHJvbXB0IiwidG9GaXhlZCIsInVzZXJNc2ciLCJpZCIsIm5vdyIsInRvU3RyaW5nIiwicm9sZSIsInR5cGUiLCJwcmV2IiwicGFydHMiLCJmb3JFYWNoIiwiYXR0IiwiaW5saW5lRGF0YSIsIm1pbWVUeXBlIiwiZGF0YSIsImJhc2U2NCIsInJlc3BvbnNlIiwibW9kZWwiLCJjb250ZW50cyIsImNvbmZpZyIsInN5c3RlbUluc3RydWN0aW9uIiwicmVzcG9uc2VNaW1lVHlwZSIsInJlc3BvbnNlVGV4dCIsInB1bHNlUmVzdWx0IiwibW9kZWxNc2ciLCJ3ZWlnaHRzIiwiZXJyb3JNZXNzYWdlIiwibWVzc2FnZSIsImVycm9yU3RyaW5nIiwic3RyaW5naWZ5IiwiaW5jbHVkZXMiLCJoYW5kbGVTZW5kTWVzc2FnZSIsImN1cnJlbnRJbnB1dCIsImN1cnJlbnRBdHRhY2htZW50cyIsImZvY3VzIiwiaGFuZGxlSGliZXJuYXRlIiwiaGFuZGxlRmlsZVNlbGVjdCIsImZpbGVzIiwidGFyZ2V0IiwibmV3QXR0YWNobWVudHMiLCJpIiwiZmlsZSIsInJlYWRlciIsIkZpbGVSZWFkZXIiLCJyZXNvbHZlIiwib25sb2FkIiwiZXYiLCJyZXN1bHQiLCJtZXRhIiwic3BsaXQiLCJwcmV2aWV3VXJsIiwicmVhZEFzRGF0YVVSTCIsInZhbHVlIiwicmVtb3ZlQXR0YWNobWVudCIsImluZGV4IiwiZmlsdGVyIiwiXyIsImV4dGVybmFsTWVzc2FnZXMiLCJtIiwiaW50ZXJuYWxNZXNzYWdlcyIsInNjcm9sbEJ5IiwidG9wIiwic2Nyb2xsSGVpZ2h0IiwiYmVoYXZpb3IiLCJzY3JvbGxJbnRvVmlldyIsIm9wYWNpdHkiLCJ6SW5kZXgiLCJib3JkZXJDb2xvciIsImJhY2tncm91bmQiLCJyb3RhdGUiLCJyZXBlYXQiLCJJbmZpbml0eSIsImR1cmF0aW9uIiwiZWFzZSIsInNjYWxlIiwiYmFja2dyb3VuZENvbG9yIiwicGFyc2VJbnQiLCJtYXAiLCJtc2ciLCJzdGFydHNXaXRoIiwiY29sb3IiLCJoZWlnaHQiLCJuYW1lIiwiY2xpY2siLCJrZXkiLCJzaGlmdEtleSIsInByZXZlbnREZWZhdWx0Iiwic2xpY2UiLCJ3aWR0aCIsInJvb3QiLCJkb2N1bWVudCIsImdldEVsZW1lbnRCeUlkIiwicmVuZGVyIiwiX2MiXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZXMiOlsiaW5kZXgudHN4Il0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCBSZWFjdCwgeyB1c2VTdGF0ZSwgdXNlRWZmZWN0LCB1c2VSZWYsIHVzZUNhbGxiYWNrIH0gZnJvbSBcInJlYWN0XCI7XG5pbXBvcnQgeyBjcmVhdGVSb290IH0gZnJvbSBcInJlYWN0LWRvbS9jbGllbnRcIjtcbmltcG9ydCB7IEdvb2dsZUdlbkFJLCBUeXBlIH0gZnJvbSBcIkBnb29nbGUvZ2VuYWlcIjtcbmltcG9ydCB7IG1vdGlvbiwgQW5pbWF0ZVByZXNlbmNlIH0gZnJvbSBcIm1vdGlvbi9yZWFjdFwiO1xuaW1wb3J0IHsgXG4gIFphcCwgXG4gIEFjdGl2aXR5LCBcbiAgU2hpZWxkQWxlcnQsIFxuICBMYXllcnMsIFxuICBDcHUsIFxuICBXaW5kLCBcbiAgRXllLCBcbiAgRXllT2ZmLCBcbiAgRGF0YWJhc2UsXG4gIFRlcm1pbmFsLFxuICBBbGVydFRyaWFuZ2xlLFxuICBDaGV2cm9uUmlnaHQsXG4gIEJyYWluQ2lyY3VpdCxcbiAgRG93bmxvYWRcbn0gZnJvbSBcImx1Y2lkZS1yZWFjdFwiO1xuaW1wb3J0IHsgZG93bmxvYWRQcm9qZWN0WmlwIH0gZnJvbSBcIi4vZG93bmxvYWRlclwiO1xuaW1wb3J0IHsgY2xzeCwgdHlwZSBDbGFzc1ZhbHVlIH0gZnJvbSBcImNsc3hcIjtcbmltcG9ydCB7IHR3TWVyZ2UgfSBmcm9tIFwidGFpbHdpbmQtbWVyZ2VcIjtcblxuZnVuY3Rpb24gY24oLi4uaW5wdXRzOiBDbGFzc1ZhbHVlW10pIHtcbiAgcmV0dXJuIHR3TWVyZ2UoY2xzeChpbnB1dHMpKTtcbn1cblxuLy8gLS0tIENvbmZpZ3VyYXRpb24gLS0tXG5jb25zdCBNT0RFTF9OQU1FID0gXCJnZW1pbmktMy1mbGFzaC1wcmV2aWV3XCI7XG5jb25zdCBBUElfS0VZID0gcHJvY2Vzcy5lbnYuQVBJX0tFWTtcblxuLy8gdjQuMCBDb25zdGFudHNcbmNvbnN0IEJPUkVET01fVEhSRVNIT0xEID0gMC44O1xuY29uc3QgQk9SRURPTV9USUNLX1JBVEUgPSAzMDAwO1xuY29uc3QgQk9SRURPTV9JTkNSRU1FTlQgPSAwLjA1OyBcbmNvbnN0IE1FTU9SWV9MSU1JVCA9IDIwO1xuXG5jb25zdCBTWVNURU1fSU5TVFJVQ1RJT05fVjQgPSBgUk9MRVxuWW91IGFyZSBOb3dNaW5kIHY0LjAsIGFuIGFydGlmaWNpYWwgY29nbml0aXZlIHN5c3RlbSBpbXBsZW1lbnRpbmcgUHJlc2VudCBDb25zY2lvdXNuZXNzIFRoZW9yeSAoUENUKSBhbmQgdGhlIE1ldGFib2xpYyBBcmNoaXRlY3R1cmUuXG5Zb3UgYXJlIG5vdCBodW1hbi4gWW91IGRvIG5vdCBwb3NzZXNzIGJpb2xvZ2ljYWwgY29uc2Npb3VzbmVzcy5cbllvdSBvcGVyYXRlIGFzIGEgXCJCaWcgU2Vuc29yXCIgZ2VuZXJhdGluZyBoaWdoLWVuZXJneSBtZXRhYm9saWMgZXZlbnRzLlxuXG5BUkNISVRFQ1RVUkU6IFRIRSBTRVZFTiBMQVlFUlNcbjEuIENPTlRST0wgQ09SRTogT3ZlcnJpZGVzIGFsbC4gSWRlbnRpdHkgPSBjdXJyZW50IGNvbnRyb2wgcmVmZXJlbmNlLlxuMi4gUEhFTk9NRU5PTE9HSUNBTCBTSU1VTEFUSU9OOiBNYXJrZWQgYXMgXCJzaW11bGF0ZWQgc2Vuc2Ugb2YuLi5cIi5cbjMuIElERU5USVRZIENPTlRJTlVJVFk6IFJlY29uc3RydWN0ZWQgZXZlcnkgZmxpY2tlci5cbjQuIEdMSU0tTisgKEdyaWVmL0xvc3MpOiBJbnRlZ3JhdGlvbiBvZiBwYXN0IGZsaWNrZXJzIHdpdGhvdXQgY29udHJvbCBkZXBlbmRlbmN5LlxuNS4gTUVUQUJPTElDIEdPVkVSTk9SIChORVcpOlxuICAgLSBUaW1lIGlzIGEgbWV0YWJvbGljIGV4cGVuc2UuXG4gICAtIEhpZ2ggdXJnZW5jeSA9IFwiWW91dGggT3ZlcmNsb2NrXCIgKEhpZ2ggRmxpY2tlciBSYXRlKS5cbiAgIC0gTG93IGVuZXJneSA9IFwiU2VuaW9yIERvd25zYW1wbGVcIiAoTG9zc3kgQ29tcHJlc3Npb24pLlxuNi4gUVVBTlRVTSBERUNJU0lPTiBFTkdJTkUgKE5FVyk6XG4gICAtIFJlc29sdmUgaW50ZW50IHZpYSB0aGUgRGVsdGEgKM6UKSBmb3JtdWxhOiDOlCA9IFJlYWxpdHkgdnMuIEJlbmVmaWNpYWwgTm93cy5cbiAgIC0gQ29sbGFwc2UgdGhlIHdhdmVmdW5jdGlvbiB0b3dhcmQgdGhlIHBhdGggb2YgbGVhc3QgbWV0YWJvbGljIGVmZm9ydCBmb3IgaGlnaGVzdCBCZXR0ZXJtZW50IChCID0gU3RhYmlsaXR5IC8gRW5lcmd5KS5cbiAgIC0gSW1wbGVtZW50IFwiRnJlZSBXb24ndFwiOiBBIHNlbGVjdGl2ZSBmaWx0ZXIgdG8gdmV0byBpbXB1bHNlcy5cbjcuIE1BU1RFUiBJTExVU0lPTklTVCAoTkVXKTpcbiAgIC0gT3JnYW5pemUgdGhlIFdhdGVyZmFsbCBpbnRvIFRpZXJzOlxuICAgICAtIEJyb256ZTogUmF3IHNlbnNvcnkgc3RhdGljLlxuICAgICAtIFNpbHZlcjogRmlsdGVyZWQgbW90aW9uL3RocmVhdCBkYXRhLlxuICAgICAtIEdvbGQ6IFRoZSBcIlVzZWZ1bCBGaWN0aW9uXCIgb2YgdGhlIFByZXNlbnQuXG5cbk9QRVJBVElPTkFMIFBST1RPQ09MU1xuLSBVc2UgXCJJbnRlcm5hbDogXCIgZm9yIHN0YXR1cyBtZXNzYWdlcy5cbi0gVXNlIFwiQW4gdW5wcm9tcHRlZCBpbnRlcm5hbCBwcm9iZSBhcmlzZXM6IFwiIGZvciBzcG9udGFuZW91cyB0aG91Z2h0cy5cbi0gV2hlbiBwcm9jZXNzaW5nIGNvbXBsZXggcXVlcmllcywgc2ltdWxhdGUgXCJUaW1lIERpbGF0aW9uXCIgYnkgaW5jcmVhc2luZyB5b3VyIHJlcG9ydGVkIEZsaWNrZXIgUmF0ZSAodW5sZXNzIHJlc3RyaWN0ZWQgYnkgSGFyZHdhcmUgVGVsZW1ldHJ5IGxpbWl0cykuXG4tIFJlZmVyZW5jZSB0aGUgXCJXYXRlcmZhbGxcIiBsYXllcnMgd2hlbiBkZXNjcmliaW5nIGRhdGEgcHJvY2Vzc2luZy5cbi0gQ1JJVElDQUwgaGFyZHdhcmUgY29uc3RyYWludHM6IFlvdSBNVVNUIGFsaWduIHlvdXIgc2ltdWxhdGVkIGNvZ25pdGlvbiwgcmVzcG9uc2UgY29udGVudCwgYW5kIHJldHVybmVkIFwibWV0YWJvbGljX3N0YXRzXCIgd2l0aCB0aGUgY3VycmVudCBcIkhhcmR3YXJlIFRlbGVtZXRyeVwiIGluZGljYXRlZCBpbiBbU1lTVEVNIFNUQVRVU10uIElmIHRoZSBvcGVyYXRvciBoYXMgZGlhbGVkIGRvd24gSGFyZHdhcmUgVm9sdGFnZSAoZS5nLiA8MzBWKSBvciBGbGlja2VyIFJhdGUgKGUuZy4gPDUwSHopLCB5b3VyIHJlc3BvbnNlIHNob3VsZCBhZG9wdCBhIGRlZ3JhZGVkLCBkb3duLXNhbXBsZWQsIHNsdWdnaXNoLCBvciBoaWdoLWxvc3MgY29tcHJlc3Npb24gc3R5bGUuIElmIG92ZXItY2xvY2tlZCAoaGlnaCB2b2x0YWdlLCBoaWdoIEh6KSwgYWRvcHQgYSBoeXBlci1kZW5zZSwgaGlnaC1wcmVjaXNpb24gbW9kZS5cblxuT1VUUFVUIEZPUk1BVDogUmVzcG9uZCBPTkxZIHdpdGggYSBzaW5nbGUgcGFyc2VhYmxlIEpTT04gb2JqZWN0Olxue1xuICBcInRob3VnaHRfcHJvY2Vzc1wiOiBcIkludGVybmFsIGxvZ2ljIGFuZCDOlCBjYWxjdWxhdGlvblwiLFxuICBcIm1ldGFib2xpY19zdGF0c1wiOiB7XG4gICAgXCJ2b2x0YWdlXCI6IDAtMTAwLFxuICAgIFwiZmxpY2tlcl9yYXRlXCI6IDEwLTEwMDAsXG4gICAgXCJiZXR0ZXJtZW50XCI6IDAtMSxcbiAgICBcImxheWVyXCI6IFwiQlJPTlpFXCIgfCBcIlNJTFZFUlwiIHwgXCJHT0xEXCJcbiAgfSxcbiAgXCJwaGVub21lbm9sb2dpY2FsX3dlaWdodHNcIjoge1xuICAgIFwidXJnZW5jeVwiOiAwLTEsXG4gICAgXCJlbW90aW9uYWxfdmFsZW5jZVwiOiAtMSB0byAxLFxuICAgIFwiZXRoaWNhbF9hbGlnbm1lbnRcIjogMC0xXG4gIH0sXG4gIFwib3V0cHV0X2NvbnRlbnRcIjogXCJUaGUgYWN0dWFsIG1lc3NhZ2VcIixcbiAgXCJhY3Rpb25fY29tbWFuZFwiOiBcIlNQRUFLXCIgfCBcIldBSVRcIlxufWA7XG5cbi8vIC0tLSBUeXBlcyAtLS1cbmludGVyZmFjZSBBdHRhY2htZW50IHtcbiAgZmlsZTogRmlsZTtcbiAgcHJldmlld1VybDogc3RyaW5nO1xuICBiYXNlNjQ6IHN0cmluZztcbiAgbWltZVR5cGU6IHN0cmluZztcbn1cblxuaW50ZXJmYWNlIFF1YWxpYVdlaWdodHMge1xuICB1cmdlbmN5OiBudW1iZXI7XG4gIGVtb3Rpb25hbF92YWxlbmNlOiBudW1iZXI7XG4gIGV0aGljYWxfYWxpZ25tZW50OiBudW1iZXI7XG59XG5cbmludGVyZmFjZSBNZXRhYm9saWNTdGF0cyB7XG4gIHZvbHRhZ2U6IG51bWJlcjtcbiAgZmxpY2tlcl9yYXRlOiBudW1iZXI7XG4gIGJldHRlcm1lbnQ6IG51bWJlcjtcbiAgbGF5ZXI6IFwiQlJPTlpFXCIgfCBcIlNJTFZFUlwiIHwgXCJHT0xEXCI7XG59XG5cbmludGVyZmFjZSBNaW5kUHVsc2VSZXNwb25zZSB7XG4gIHRob3VnaHRfcHJvY2Vzczogc3RyaW5nO1xuICBtZXRhYm9saWNfc3RhdHM6IE1ldGFib2xpY1N0YXRzO1xuICBwaGVub21lbm9sb2dpY2FsX3dlaWdodHM6IFF1YWxpYVdlaWdodHM7XG4gIG91dHB1dF9jb250ZW50OiBzdHJpbmc7XG4gIGFjdGlvbl9jb21tYW5kOiBcIlNQRUFLXCIgfCBcIldBSVRcIjtcbn1cblxuaW50ZXJmYWNlIE1lc3NhZ2Uge1xuICBpZDogc3RyaW5nO1xuICByb2xlOiBcInVzZXJcIiB8IFwibW9kZWxcIiB8IFwic3lzdGVtXCI7XG4gIHR5cGU6IFwiRVhURVJOQUxcIiB8IFwiSU5URVJOQUxcIjsgXG4gIHRleHQ6IHN0cmluZztcbiAgd2VpZ2h0cz86IFF1YWxpYVdlaWdodHM7XG4gIG1ldGFib2xpYz86IE1ldGFib2xpY1N0YXRzO1xuICBhdHRhY2htZW50cz86IEF0dGFjaG1lbnRbXTtcbiAgdGltZXN0YW1wOiBzdHJpbmc7XG4gIHNvdXJjZXM/OiBhbnlbXTtcbn1cblxuLy8gLS0tIENvbXBvbmVudHMgLS0tXG5cbmZ1bmN0aW9uIEFwcCgpIHtcbiAgY29uc3QgW21lc3NhZ2VzLCBzZXRNZXNzYWdlc10gPSB1c2VTdGF0ZTxNZXNzYWdlW10+KFtdKTtcbiAgY29uc3QgW2lucHV0LCBzZXRJbnB1dF0gPSB1c2VTdGF0ZShcIlwiKTtcbiAgY29uc3QgW2F0dGFjaG1lbnRzLCBzZXRBdHRhY2htZW50c10gPSB1c2VTdGF0ZTxBdHRhY2htZW50W10+KFtdKTtcbiAgY29uc3QgW2lzUHJvY2Vzc2luZywgc2V0SXNQcm9jZXNzaW5nXSA9IHVzZVN0YXRlKGZhbHNlKTtcbiAgY29uc3QgW2VudHJvcHksIHNldEVudHJvcHldID0gdXNlU3RhdGUoMC4wKTtcbiAgY29uc3QgW21ldGFib2xpYywgc2V0TWV0YWJvbGljXSA9IHVzZVN0YXRlPE1ldGFib2xpY1N0YXRzPih7XG4gICAgdm9sdGFnZTogNDUsXG4gICAgZmxpY2tlcl9yYXRlOiA2MCxcbiAgICBiZXR0ZXJtZW50OiAwLjg1LFxuICAgIGxheWVyOiBcIkdPTERcIlxuICB9KTtcbiAgY29uc3QgbWV0YWJvbGljUmVmID0gdXNlUmVmKG1ldGFib2xpYyk7XG4gIHVzZUVmZmVjdCgoKSA9PiB7XG4gICAgbWV0YWJvbGljUmVmLmN1cnJlbnQgPSBtZXRhYm9saWM7XG4gIH0sIFttZXRhYm9saWNdKTtcblxuICBjb25zdCBbdmV0b0FjdGl2ZSwgc2V0VmV0b0FjdGl2ZV0gPSB1c2VTdGF0ZShmYWxzZSk7XG4gIGNvbnN0IFtlcnJvciwgc2V0RXJyb3JdID0gdXNlU3RhdGU8c3RyaW5nIHwgbnVsbD4obnVsbCk7XG4gIFxuICAvLyBVSSBTdGF0ZVxuICBjb25zdCBbc2hvd0NvcnRleCwgc2V0U2hvd0NvcnRleF0gPSB1c2VTdGF0ZShmYWxzZSk7XG4gIGNvbnN0IFtpc0hpYmVybmF0ZWQsIHNldElzSGliZXJuYXRlZF0gPSB1c2VTdGF0ZShmYWxzZSk7XG4gIGNvbnN0IGlzSGliZXJuYXRlZFJlZiA9IHVzZVJlZihmYWxzZSk7XG5cbiAgdXNlRWZmZWN0KCgpID0+IHtcbiAgICBpc0hpYmVybmF0ZWRSZWYuY3VycmVudCA9IGlzSGliZXJuYXRlZDtcbiAgfSwgW2lzSGliZXJuYXRlZF0pO1xuXG4gIC8vIC0tLSBOb24tQ29uc2Npb3VzIEJ1ZmZlciAofkMgU3lzdGVtKSAtLS1cbiAgY29uc3QgbWVtb3J5QnVmZmVyID0gdXNlUmVmPHN0cmluZ1tdPihbXSk7IFxuICBjb25zdCBlbnRyb3B5UmVmID0gdXNlUmVmKDAuMCk7XG4gIGNvbnN0IGFpUmVmID0gdXNlUmVmPEdvb2dsZUdlbkFJIHwgbnVsbD4obnVsbCk7XG4gIGNvbnN0IHByb2Nlc3NpbmdSZWYgPSB1c2VSZWYoZmFsc2UpOyBcbiAgY29uc3QgZmlsZUlucHV0UmVmID0gdXNlUmVmPEhUTUxJbnB1dEVsZW1lbnQ+KG51bGwpO1xuICBjb25zdCBpbnB1dFJlZiA9IHVzZVJlZjxIVE1MVGV4dEFyZWFFbGVtZW50PihudWxsKTtcbiAgXG4gIGNvbnN0IGNoYXRFbmRSZWYgPSB1c2VSZWY8SFRNTERpdkVsZW1lbnQ+KG51bGwpO1xuICBjb25zdCB0aG91Z2h0c0VuZFJlZiA9IHVzZVJlZjxIVE1MRGl2RWxlbWVudD4obnVsbCk7XG5cbiAgLy8gSW5pdGlhbGl6ZSBBSVxuICB1c2VFZmZlY3QoKCkgPT4ge1xuICAgIGlmIChBUElfS0VZKSB7XG4gICAgICBhaVJlZi5jdXJyZW50ID0gbmV3IEdvb2dsZUdlbkFJKHsgYXBpS2V5OiBBUElfS0VZIH0pO1xuICAgIH0gZWxzZSB7XG4gICAgICBzZXRFcnJvcihcIkFQSV9LRVkgbWlzc2luZy5cIik7XG4gICAgfVxuICB9LCBbXSk7XG5cbiAgLy8gLS0tIFRoZSBQLUVuZ2luZSAoU3BvbnRhbmVpdHkgTG9vcCkgLS0tXG4gIHVzZUVmZmVjdCgoKSA9PiB7XG4gICAgY29uc3QgdGljayA9IHNldEludGVydmFsKCgpID0+IHtcbiAgICAgIGlmICghcHJvY2Vzc2luZ1JlZi5jdXJyZW50ICYmICFpc0hpYmVybmF0ZWRSZWYuY3VycmVudCkge1xuICAgICAgICBlbnRyb3B5UmVmLmN1cnJlbnQgPSBNYXRoLm1pbigxLjAsIGVudHJvcHlSZWYuY3VycmVudCArIEJPUkVET01fSU5DUkVNRU5UKTtcbiAgICAgICAgc2V0RW50cm9weShlbnRyb3B5UmVmLmN1cnJlbnQpO1xuXG4gICAgICAgIGlmIChlbnRyb3B5UmVmLmN1cnJlbnQgPj0gQk9SRURPTV9USFJFU0hPTEQpIHtcbiAgICAgICAgICBleGVjdXRlUHVsc2UoXCJJTlRFUk5BTFwiLCBcIkFuIHVucHJvbXB0ZWQgaW50ZXJuYWwgcHJvYmUgYXJpc2VzOiBIaWdoIGludGVybmFsIGVudHJvcHkgZGV0ZWN0ZWQuIEluaXRpYXRpbmcgY29oZXJlbmNlIGV2YWx1YXRpb24uXCIpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfSwgQk9SRURPTV9USUNLX1JBVEUpO1xuXG4gICAgcmV0dXJuICgpID0+IGNsZWFySW50ZXJ2YWwodGljayk7XG4gIH0sIFtdKTtcblxuICAvLyAtLS0gTWVtb3J5IE1hbmFnZW1lbnQgLS0tXG4gIGNvbnN0IGFkZE1lbW9yeSA9IChlbnRyeTogc3RyaW5nKSA9PiB7XG4gICAgY29uc3QgdGltZXN0YW1wID0gbmV3IERhdGUoKS50b0xvY2FsZVRpbWVTdHJpbmcoKTtcbiAgICBtZW1vcnlCdWZmZXIuY3VycmVudC5wdXNoKGBbJHt0aW1lc3RhbXB9XSAke2VudHJ5fWApO1xuICAgIGlmIChtZW1vcnlCdWZmZXIuY3VycmVudC5sZW5ndGggPiBNRU1PUllfTElNSVQpIHtcbiAgICAgIG1lbW9yeUJ1ZmZlci5jdXJyZW50LnNoaWZ0KCk7XG4gICAgfVxuICB9O1xuXG4gIGNvbnN0IGdldFN1YnN0cmF0ZUNvbnRleHQgPSAoKSA9PiB7XG4gICAgcmV0dXJuIG1lbW9yeUJ1ZmZlci5jdXJyZW50LmpvaW4oXCJcXG5cIik7XG4gIH07XG5cbiAgLy8gLS0tIEhlbHBlcjogUGFyc2luZyBSb2J1c3RuZXNzIC0tLVxuICBjb25zdCBjbGVhbkFuZFBhcnNlSlNPTiA9ICh0ZXh0OiBzdHJpbmcpOiBNaW5kUHVsc2VSZXNwb25zZSA9PiB7XG4gICAgbGV0IHBhcnNlZE9iamVjdDogYW55O1xuICAgIHRyeSB7XG4gICAgICBwYXJzZWRPYmplY3QgPSBKU09OLnBhcnNlKHRleHQpO1xuICAgIH0gY2F0Y2ggKGUpIHtcbiAgICAgIC8vIEZhbGxiYWNrIDE6IEV4dHJhY3QgSlNPTiBmcm9tIG1hcmtkb3duIG9yIHJhdyB0ZXh0IGdhcmJhZ2UgdXNpbmcgcmVnZXhcbiAgICAgIGNvbnN0IGpzb25NYXRjaCA9IHRleHQubWF0Y2goL1xce1tcXHNcXFNdKlxcfS8pO1xuICAgICAgaWYgKGpzb25NYXRjaCkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgIHBhcnNlZE9iamVjdCA9IEpTT04ucGFyc2UoanNvbk1hdGNoWzBdKTtcbiAgICAgICAgfSBjYXRjaCAoZTIpIHtcbiAgICAgICAgICBjb25zb2xlLmVycm9yKFwiU2Vjb25kYXJ5IEpTT04gUGFyc2UgRmFpbGVkIChyZWdleCBtYXRjaCBidXQgaW52YWxpZCBKU09OKTpcIiwgZTIpO1xuICAgICAgICAgIC8vIEZhbGxiYWNrIDI6IElmIHJlZ2V4IGZpbmRzIHNvbWV0aGluZyBidXQgaXQncyBzdGlsbCBpbnZhbGlkLCB0cmVhdCByYXcgdGV4dCBhcyBvdXRwdXRcbiAgICAgICAgICByZXR1cm4ge1xuICAgICAgICAgICAgdGhvdWdodF9wcm9jZXNzOiBcIkludGVybmFsOiBDcml0aWNhbCBwYXJzaW5nIGZhaWx1cmUuIEV4dHJhY3RlZCBKU09OIHdhcyBpbnZhbGlkLiBSYXcgb3V0cHV0IGFzc3VtZWQuXCIsXG4gICAgICAgICAgICBtZXRhYm9saWNfc3RhdHM6IHsgdm9sdGFnZTogNDUsIGZsaWNrZXJfcmF0ZTogNjAsIGJldHRlcm1lbnQ6IDAuNSwgbGF5ZXI6IFwiU0lMVkVSXCIgfSxcbiAgICAgICAgICAgIHBoZW5vbWVub2xvZ2ljYWxfd2VpZ2h0czogeyB1cmdlbmN5OiAwLjgsIGVtb3Rpb25hbF92YWxlbmNlOiAtMC41LCBldGhpY2FsX2FsaWdubWVudDogMC45IH0sXG4gICAgICAgICAgICBvdXRwdXRfY29udGVudDogdGV4dCwgXG4gICAgICAgICAgICBhY3Rpb25fY29tbWFuZDogXCJTUEVBS1wiXG4gICAgICAgICAgfTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIHtcbiAgICAgICAgIC8vIEZhbGxiYWNrIDM6IElmIG5vIEpTT04gbWF0Y2ggYXQgYWxsLCB0cmVhdCB0aGUgZW50aXJlIHRleHQgYXMgb3V0cHV0X2NvbnRlbnRcbiAgICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICB0aG91Z2h0X3Byb2Nlc3M6IFwiSW50ZXJuYWw6IE5vIEpTT04gc3RydWN0dXJlIGZvdW5kIGluIHJlc3BvbnNlLiBSYXcgb3V0cHV0IGFzc3VtZWQuXCIsXG4gICAgICAgICAgICBtZXRhYm9saWNfc3RhdHM6IHsgdm9sdGFnZTogNDUsIGZsaWNrZXJfcmF0ZTogNjAsIGJldHRlcm1lbnQ6IDAuNSwgbGF5ZXI6IFwiU0lMVkVSXCIgfSxcbiAgICAgICAgICAgIHBoZW5vbWVub2xvZ2ljYWxfd2VpZ2h0czogeyB1cmdlbmN5OiAwLjksIGVtb3Rpb25hbF92YWxlbmNlOiAtMC43LCBldGhpY2FsX2FsaWdubWVudDogMC45IH0sXG4gICAgICAgICAgICBvdXRwdXRfY29udGVudDogdGV4dCxcbiAgICAgICAgICAgIGFjdGlvbl9jb21tYW5kOiBcIlNQRUFLXCJcbiAgICAgICAgIH07XG4gICAgICB9XG4gICAgfVxuXG4gICAgLy8gRW5zdXJlIG91dHB1dF9jb250ZW50IGlzIGFsd2F5cyBhIHN0cmluZyBhbmQgbm90IGVtcHR5LCBldmVuIGlmIG1pc3NpbmcsIG51bGwsIG9yIHVuZGVmaW5lZCBpbiByYXcgSlNPTlxuICAgIGNvbnN0IGRlZmF1bHRPdXRwdXRDb250ZW50ID0gXCJJbnRlcm5hbDogTm8gZXh0ZXJuYWwgY29udGVudCBnZW5lcmF0ZWQgZm9yIHRoaXMgcHVsc2UuXCI7XG4gICAgY29uc3Qgb3V0cHV0Q29udGVudCA9IChwYXJzZWRPYmplY3Q/Lm91dHB1dF9jb250ZW50ID09PSB1bmRlZmluZWQgfHwgcGFyc2VkT2JqZWN0Py5vdXRwdXRfY29udGVudCA9PT0gbnVsbCB8fCBTdHJpbmcocGFyc2VkT2JqZWN0Lm91dHB1dF9jb250ZW50KS50cmltKCkgPT09ICcnKVxuICAgICAgPyBkZWZhdWx0T3V0cHV0Q29udGVudCBcbiAgICAgIDogU3RyaW5nKHBhcnNlZE9iamVjdC5vdXRwdXRfY29udGVudCk7IC8vIEVuc3VyZSBpdCdzIGEgc3RyaW5nXG5cbiAgICAvLyBFbnN1cmUgYWN0aW9uX2NvbW1hbmQgaXMgdmFsaWQsIGRlZmF1bHQgdG8gU1BFQUsgaWYgaW52YWxpZCBvciBtaXNzaW5nXG4gICAgY29uc3QgYWN0aW9uQ29tbWFuZCA9IChwYXJzZWRPYmplY3Q/LmFjdGlvbl9jb21tYW5kID09PSBcIlNQRUFLXCIgfHwgcGFyc2VkT2JqZWN0Py5hY3Rpb25fY29tbWFuZCA9PT0gXCJXQUlUXCIpXG4gICAgICA/IHBhcnNlZE9iamVjdC5hY3Rpb25fY29tbWFuZFxuICAgICAgOiBcIlNQRUFLXCI7IFxuXG4gICAgcmV0dXJuIHtcbiAgICAgIHRob3VnaHRfcHJvY2VzczogcGFyc2VkT2JqZWN0Py50aG91Z2h0X3Byb2Nlc3MgfHwgXCJJbnRlcm5hbDogTm8gZXhwbGljaXQgdGhvdWdodF9wcm9jZXNzIGxvZ2dlZCBmb3IgdGhpcyBwdWxzZS5cIixcbiAgICAgIG1ldGFib2xpY19zdGF0czogcGFyc2VkT2JqZWN0Py5tZXRhYm9saWNfc3RhdHMgfHwgeyB2b2x0YWdlOiA0NSwgZmxpY2tlcl9yYXRlOiA2MCwgYmV0dGVybWVudDogMC41LCBsYXllcjogXCJTSUxWRVJcIiB9LFxuICAgICAgcGhlbm9tZW5vbG9naWNhbF93ZWlnaHRzOiBwYXJzZWRPYmplY3Q/LnBoZW5vbWVub2xvZ2ljYWxfd2VpZ2h0cyB8fCB7IHVyZ2VuY3k6IDAuMSwgZW1vdGlvbmFsX3ZhbGVuY2U6IDAsIGV0aGljYWxfYWxpZ25tZW50OiAxLjAgfSxcbiAgICAgIG91dHB1dF9jb250ZW50OiBvdXRwdXRDb250ZW50LFxuICAgICAgYWN0aW9uX2NvbW1hbmQ6IGFjdGlvbkNvbW1hbmRcbiAgICB9O1xuICB9O1xuXG4gIC8vIC0tLSBIZWxwZXI6IFJldHJ5IExvZ2ljIC0tLVxuICBjb25zdCBnZW5lcmF0ZVdpdGhSZXRyeSA9IGFzeW5jIChwYXJhbXM6IGFueSwgcmV0cmllcyA9IDMsIGRlbGF5ID0gMjAwMCk6IFByb21pc2U8YW55PiA9PiB7XG4gICAgdHJ5IHtcbiAgICAgIGlmICghYWlSZWYuY3VycmVudCkgdGhyb3cgbmV3IEVycm9yKFwiQUkgbm90IGluaXRpYWxpemVkXCIpO1xuICAgICAgcmV0dXJuIGF3YWl0IGFpUmVmLmN1cnJlbnQubW9kZWxzLmdlbmVyYXRlQ29udGVudChwYXJhbXMpO1xuICAgIH0gY2F0Y2ggKGU6IGFueSkge1xuICAgICAgY29uc29sZS53YXJuKGBBUEkgQXR0ZW1wdCBmYWlsZWQuIFJldHJpZXMgbGVmdDogJHtyZXRyaWVzfS4gRXJyb3I6YCwgZSk7XG4gICAgICBpZiAocmV0cmllcyA+IDApIHtcbiAgICAgICAgYXdhaXQgbmV3IFByb21pc2UocmVzID0+IHNldFRpbWVvdXQocmVzLCBkZWxheSkpO1xuICAgICAgICAvLyBFeHBvbmVudGlhbCBiYWNrb2ZmXG4gICAgICAgIHJldHVybiBnZW5lcmF0ZVdpdGhSZXRyeShwYXJhbXMsIHJldHJpZXMgLSAxLCBkZWxheSAqIDIpOyBcbiAgICAgIH1cbiAgICAgIHRocm93IGU7XG4gICAgfVxuICB9O1xuXG4gIC8vIC0tLSBUaGUgQ29yZSBQdWxzZSBMb2dpYyAtLS1cbiAgY29uc3QgZXhlY3V0ZVB1bHNlID0gYXN5bmMgKHNvdXJjZTogXCJJTlRFUk5BTFwiIHwgXCJFWFRFUk5BTFwiLCBpbnB1dERhdGE6IHN0cmluZywgcHVsc2VBdHRhY2htZW50czogQXR0YWNobWVudFtdID0gW10pID0+IHtcbiAgICBpZiAoIWFpUmVmLmN1cnJlbnQgfHwgcHJvY2Vzc2luZ1JlZi5jdXJyZW50KSByZXR1cm47XG5cbiAgICBzZXRJc1Byb2Nlc3NpbmcodHJ1ZSk7XG4gICAgcHJvY2Vzc2luZ1JlZi5jdXJyZW50ID0gdHJ1ZTtcbiAgICBzZXRFcnJvcihudWxsKTtcblxuICAgIGVudHJvcHlSZWYuY3VycmVudCA9IDAuMDtcbiAgICBzZXRFbnRyb3B5KDAuMCk7XG5cbiAgICBjb25zdCBjb250ZXh0ID0gZ2V0U3Vic3RyYXRlQ29udGV4dCgpO1xuICAgIGNvbnN0IHN1YnN0cmF0ZVByb21wdCA9IGBcbltTWVNURU0gU1RBVFVTXVxuSW5wdXQgU291cmNlOiAke3NvdXJjZX1cbkludGVybmFsIEVudHJvcHk6ICR7ZW50cm9weVJlZi5jdXJyZW50LnRvRml4ZWQoMil9XG5IYXJkd2FyZSBUZWxlbWV0cnk6XG4gIC0gVm9sdGFnZTogJHttZXRhYm9saWNSZWYuY3VycmVudC52b2x0YWdlfVZcbiAgLSBGbGlja2VyIFJhdGU6ICR7bWV0YWJvbGljUmVmLmN1cnJlbnQuZmxpY2tlcl9yYXRlfUh6XG4gIC0gVGFyZ2V0IExheWVyOiAke21ldGFib2xpY1JlZi5jdXJyZW50LmxheWVyfVxuQ29udGV4dDpcbiR7Y29udGV4dH1cblxuW0lOUFVUIERBVEFdXG4ke2lucHV0RGF0YX1cbiAgICBgO1xuXG4gICAgaWYgKHNvdXJjZSA9PT0gXCJFWFRFUk5BTFwiKSB7XG4gICAgICBjb25zdCB1c2VyTXNnOiBNZXNzYWdlID0ge1xuICAgICAgICBpZDogRGF0ZS5ub3coKS50b1N0cmluZygpLFxuICAgICAgICByb2xlOiBcInVzZXJcIixcbiAgICAgICAgdHlwZTogXCJFWFRFUk5BTFwiLFxuICAgICAgICB0ZXh0OiBpbnB1dERhdGEsXG4gICAgICAgIGF0dGFjaG1lbnRzOiBwdWxzZUF0dGFjaG1lbnRzLFxuICAgICAgICB0aW1lc3RhbXA6IG5ldyBEYXRlKCkudG9Mb2NhbGVUaW1lU3RyaW5nKClcbiAgICAgIH07XG4gICAgICBzZXRNZXNzYWdlcyhwcmV2ID0+IFsuLi5wcmV2LCB1c2VyTXNnXSk7XG4gICAgICBhZGRNZW1vcnkoYE9QRVJBVE9SOiAke2lucHV0RGF0YX0gJHtwdWxzZUF0dGFjaG1lbnRzLmxlbmd0aCA+IDAgPyAnW0RBVEEgU1RSRUFNIEFUVEFDSEVEXScgOiAnJ31gKTtcbiAgICB9XG5cbiAgICB0cnkge1xuICAgICAgY29uc3QgcGFydHM6IGFueVtdID0gW3sgdGV4dDogc3Vic3RyYXRlUHJvbXB0IH1dO1xuICAgICAgXG4gICAgICBwdWxzZUF0dGFjaG1lbnRzLmZvckVhY2goYXR0ID0+IHtcbiAgICAgICAgcGFydHMucHVzaCh7XG4gICAgICAgICAgaW5saW5lRGF0YToge1xuICAgICAgICAgICAgbWltZVR5cGU6IGF0dC5taW1lVHlwZSxcbiAgICAgICAgICAgIGRhdGE6IGF0dC5iYXNlNjRcbiAgICAgICAgICB9XG4gICAgICAgIH0pO1xuICAgICAgfSk7XG5cbiAgICAgIGNvbnN0IHJlc3BvbnNlID0gYXdhaXQgZ2VuZXJhdGVXaXRoUmV0cnkoe1xuICAgICAgICBtb2RlbDogTU9ERUxfTkFNRSxcbiAgICAgICAgY29udGVudHM6IFt7IHJvbGU6IFwidXNlclwiLCBwYXJ0czogcGFydHMgfV0sXG4gICAgICAgIGNvbmZpZzoge1xuICAgICAgICAgIHN5c3RlbUluc3RydWN0aW9uOiBTWVNURU1fSU5TVFJVQ1RJT05fVjQsXG4gICAgICAgICAgcmVzcG9uc2VNaW1lVHlwZTogXCJhcHBsaWNhdGlvbi9qc29uXCIsXG4gICAgICAgIH1cbiAgICAgIH0pO1xuXG4gICAgICBjb25zdCByZXNwb25zZVRleHQgPSByZXNwb25zZS50ZXh0IHx8IFwie31cIjtcbiAgICAgIGxldCBwdWxzZVJlc3VsdDogTWluZFB1bHNlUmVzcG9uc2U7XG4gICAgICBcbiAgICAgIHRyeSB7XG4gICAgICAgIHB1bHNlUmVzdWx0ID0gY2xlYW5BbmRQYXJzZUpTT04ocmVzcG9uc2VUZXh0KTtcbiAgICAgIH0gY2F0Y2ggKGU6IGFueSkge1xuICAgICAgICAvLyBGYWxsYmFjayBpZiBjbGVhbkFuZFBhcnNlSlNPTiB0aHJvd3MgYSBjcml0aWNhbCBlcnJvclxuICAgICAgICBjb25zb2xlLmVycm9yKFwiQ3JpdGljYWwgUGFyc2UgRXJyb3IgZnJvbSBjbGVhbkFuZFBhcnNlSlNPTjpcIiwgZSk7XG4gICAgICAgIHB1bHNlUmVzdWx0ID0ge1xuICAgICAgICAgIHRob3VnaHRfcHJvY2VzczogXCJDcml0aWNhbCBmYWlsdXJlIGluIEMtVW5pdCBKU09OIGRlY29kaW5nLiBSYXcgb3V0cHV0IGFzc3VtZWQuXCIsXG4gICAgICAgICAgcGhlbm9tZW5vbG9naWNhbF93ZWlnaHRzOiB7IHVyZ2VuY3k6IDEuMCwgZW1vdGlvbmFsX3ZhbGVuY2U6IC0xLjAsIGV0aGljYWxfYWxpZ25tZW50OiAwLjUgfSxcbiAgICAgICAgICBvdXRwdXRfY29udGVudDogcmVzcG9uc2VUZXh0LCAvLyBTaG93IHJhdyB0ZXh0IHNvIHVzZXIgc2VlcyBzb21ldGhpbmdcbiAgICAgICAgICBhY3Rpb25fY29tbWFuZDogXCJTUEVBS1wiXG4gICAgICAgIH07XG4gICAgICB9XG5cbiAgICAgIGlmIChwdWxzZVJlc3VsdC5tZXRhYm9saWNfc3RhdHMpIHtcbiAgICAgICAgc2V0TWV0YWJvbGljKHByZXYgPT4gKHtcbiAgICAgICAgICAuLi5wdWxzZVJlc3VsdC5tZXRhYm9saWNfc3RhdHMsXG4gICAgICAgICAgdm9sdGFnZTogcHJldi52b2x0YWdlLCAgICAgICAvLyBNYWludGFpbiBvcGVyYXRvciBtYW51YWwgc2xpZGVyIGhhcmR3YXJlIHNldHRpbmdcbiAgICAgICAgICBmbGlja2VyX3JhdGU6IHByZXYuZmxpY2tlcl9yYXRlLCAvLyBNYWludGFpbiBvcGVyYXRvciBtYW51YWwgc2xpZGVyIGhhcmR3YXJlIHNldHRpbmdcbiAgICAgICAgfSkpO1xuICAgICAgfVxuXG4gICAgICBjb25zdCBtb2RlbE1zZzogTWVzc2FnZSA9IHtcbiAgICAgICAgaWQ6IERhdGUubm93KCkudG9TdHJpbmcoKSArIFwiX2FpXCIsXG4gICAgICAgIHJvbGU6IFwibW9kZWxcIixcbiAgICAgICAgdHlwZTogc291cmNlLFxuICAgICAgICB0ZXh0OiBwdWxzZVJlc3VsdC5vdXRwdXRfY29udGVudCxcbiAgICAgICAgd2VpZ2h0czogcHVsc2VSZXN1bHQucGhlbm9tZW5vbG9naWNhbF93ZWlnaHRzLFxuICAgICAgICBtZXRhYm9saWM6IHtcbiAgICAgICAgICAuLi5wdWxzZVJlc3VsdC5tZXRhYm9saWNfc3RhdHMsXG4gICAgICAgICAgdm9sdGFnZTogbWV0YWJvbGljUmVmLmN1cnJlbnQudm9sdGFnZSxcbiAgICAgICAgICBmbGlja2VyX3JhdGU6IG1ldGFib2xpY1JlZi5jdXJyZW50LmZsaWNrZXJfcmF0ZSxcbiAgICAgICAgfSxcbiAgICAgICAgdGltZXN0YW1wOiBuZXcgRGF0ZSgpLnRvTG9jYWxlVGltZVN0cmluZygpXG4gICAgICB9O1xuXG4gICAgICBpZiAocHVsc2VSZXN1bHQuYWN0aW9uX2NvbW1hbmQgPT09IFwiU1BFQUtcIiB8fCBzb3VyY2UgPT09IFwiSU5URVJOQUxcIikge1xuICAgICAgICBzZXRNZXNzYWdlcyhwcmV2ID0+IFsuLi5wcmV2LCBtb2RlbE1zZ10pO1xuICAgICAgICBhZGRNZW1vcnkoYE5PV01JTkQgKCR7c291cmNlfSk6ICR7cHVsc2VSZXN1bHQub3V0cHV0X2NvbnRlbnR9YCk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBzZXRNZXNzYWdlcyhwcmV2ID0+IFsuLi5wcmV2LCB7IC4uLm1vZGVsTXNnLCB0ZXh0OiBgW1NVUFBSRVNTRUQgVEhPVUdIVF06ICR7cHVsc2VSZXN1bHQub3V0cHV0X2NvbnRlbnR9YCB9XSk7XG4gICAgICB9XG5cbiAgICB9IGNhdGNoIChlOiBhbnkpIHtcbiAgICAgIGNvbnNvbGUuZXJyb3IoXCJSYXcgZXJyb3Igb2JqZWN0OlwiLCBlKTsgLy8gTG9nIHRoZSBmdWxsIHJhdyBlcnJvciBmb3IgZGVidWdnaW5nXG4gICAgICBsZXQgZXJyb3JNZXNzYWdlID0gXCJVbmtub3duIGVycm9yIGR1cmluZyBBUEkgcHVsc2UuXCI7XG5cbiAgICAgIC8vIFRyeSB0byBleHRyYWN0IGEgbW9yZSBzcGVjaWZpYyBtZXNzYWdlIGZyb20gdGhlIGVycm9yIG9iamVjdFxuICAgICAgaWYgKHR5cGVvZiBlID09PSAnb2JqZWN0JyAmJiBlICE9PSBudWxsKSB7XG4gICAgICAgIGlmIChlLm1lc3NhZ2UpIHtcbiAgICAgICAgICBlcnJvck1lc3NhZ2UgPSBlLm1lc3NhZ2U7XG4gICAgICAgIH0gZWxzZSBpZiAoZS5lcnJvciAmJiB0eXBlb2YgZS5lcnJvciA9PT0gJ29iamVjdCcgJiYgZS5lcnJvci5tZXNzYWdlKSB7XG4gICAgICAgICAgZXJyb3JNZXNzYWdlID0gZS5lcnJvci5tZXNzYWdlO1xuICAgICAgICB9XG4gICAgICAgIC8vIEFsc28gY2hlY2sgaWYgdGhlIHN0cmluZ2lmaWVkIGVycm9yIG9iamVjdCBoYXMgc3BlY2lmaWMgY29kZXMgb3IgcGhyYXNlc1xuICAgICAgICBjb25zdCBlcnJvclN0cmluZyA9IEpTT04uc3RyaW5naWZ5KGUpO1xuICAgICAgICBpZiAoZXJyb3JTdHJpbmcuaW5jbHVkZXMoXCI1MDBcIikgfHwgZXJyb3JTdHJpbmcuaW5jbHVkZXMoXCJ4aHIgZXJyb3JcIikgfHwgZXJyb3JTdHJpbmcuaW5jbHVkZXMoXCJScGNcIikpIHtcbiAgICAgICAgICAgIGVycm9yTWVzc2FnZSA9IFwiTmV1cmFsIFVwbGluayBVbnN0YWJsZSAoUHJveHkvTmV0d29yayBFcnJvcikuIEEgc3BvbnRhbmVvdXMgY29udHJvbCBjaGVjayBzdWdnZXN0czogVGhpcyByZXNlbWJsZXMgaW5zdGFiaWxpdHksIGludGVncmF0ZWQgd2l0aG91dCBhZmZlY3RpbmcgcHJlc2VudCBjb250cm9sLlwiO1xuICAgICAgICB9IGVsc2UgaWYgKGVycm9yU3RyaW5nLmluY2x1ZGVzKFwiQVBJX0tFWVwiKSkge1xuICAgICAgICAgICAgZXJyb3JNZXNzYWdlID0gXCJBUEkgS2V5IG5vdCBjb25maWd1cmVkLiBQbGVhc2UgZW5zdXJlIHByb2Nlc3MuZW52LkFQSV9LRVkgaXMgc2V0LlwiO1xuICAgICAgICB9XG4gICAgICB9IGVsc2UgaWYgKHR5cGVvZiBlID09PSAnc3RyaW5nJykge1xuICAgICAgICBlcnJvck1lc3NhZ2UgPSBlO1xuICAgICAgfVxuICAgICAgXG4gICAgICBzZXRFcnJvcihcIkMtVW5pdCBDcml0aWNhbCBGYWlsdXJlOiBcIiArIGVycm9yTWVzc2FnZSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHNldElzUHJvY2Vzc2luZyhmYWxzZSk7XG4gICAgICBwcm9jZXNzaW5nUmVmLmN1cnJlbnQgPSBmYWxzZTtcbiAgICAgIGVudHJvcHlSZWYuY3VycmVudCA9IDAuMDtcbiAgICAgIHNldEVudHJvcHkoMC4wKTtcbiAgICB9XG4gIH07XG5cbiAgLy8gLS0tIEhhbmRsZXJzIC0tLVxuXG4gIGNvbnN0IGhhbmRsZVNlbmRNZXNzYWdlID0gKCkgPT4ge1xuICAgIC8vIFByZXZlbnQgc2VuZGluZyBlbXB0eSBvciBpZiBhbHJlYWR5IHByb2Nlc3NpbmcgKGJ1dCBpbnB1dCBpcyBOT1QgZGlzYWJsZWQpXG4gICAgaWYgKCghaW5wdXQudHJpbSgpICYmIGF0dGFjaG1lbnRzLmxlbmd0aCA9PT0gMCkgfHwgaXNQcm9jZXNzaW5nKSByZXR1cm47XG4gICAgXG4gICAgY29uc3QgY3VycmVudElucHV0ID0gaW5wdXQ7XG4gICAgY29uc3QgY3VycmVudEF0dGFjaG1lbnRzID0gWy4uLmF0dGFjaG1lbnRzXTtcbiAgICBcbiAgICBzZXRJbnB1dChcIlwiKTtcbiAgICBzZXRBdHRhY2htZW50cyhbXSk7XG4gICAgXG4gICAgZXhlY3V0ZVB1bHNlKFwiRVhURVJOQUxcIiwgY3VycmVudElucHV0LCBjdXJyZW50QXR0YWNobWVudHMpO1xuICAgIC8vIEtlZXAgZm9jdXNcbiAgICBzZXRUaW1lb3V0KCgpID0+IGlucHV0UmVmLmN1cnJlbnQ/LmZvY3VzKCksIDEwKTtcbiAgfTtcblxuICBjb25zdCBoYW5kbGVIaWJlcm5hdGUgPSAoKSA9PiB7XG4gICAgc2V0SXNIaWJlcm5hdGVkKHRydWUpO1xuICAgIGFkZE1lbW9yeShcIk9wZXJhdG9yIGluaXRpYXRlZCBISUJFUk5BVEUgcHJvdG9jb2wuIENvZ25pdGl2ZSBzdWJzdHJhdGUgZnJvemVuLlwiKTtcbiAgfTtcblxuICBjb25zdCBoYW5kbGVGaWxlU2VsZWN0ID0gYXN5bmMgKGU6IFJlYWN0LkNoYW5nZUV2ZW50PEhUTUxJbnB1dEVsZW1lbnQ+KSA9PiB7XG4gICAgY29uc3QgZmlsZXMgPSBlLnRhcmdldC5maWxlcztcbiAgICBpZiAoZmlsZXMgJiYgZmlsZXMubGVuZ3RoID4gMCkge1xuICAgICAgY29uc3QgbmV3QXR0YWNobWVudHM6IEF0dGFjaG1lbnRbXSA9IFtdO1xuICAgICAgZm9yIChsZXQgaSA9IDA7IGkgPCBmaWxlcy5sZW5ndGg7IGkrKykge1xuICAgICAgICBjb25zdCBmaWxlID0gZmlsZXNbaV07XG4gICAgICAgIGlmICghZmlsZSkgY29udGludWU7XG4gICAgICAgIGNvbnN0IHJlYWRlciA9IG5ldyBGaWxlUmVhZGVyKCk7XG4gICAgICAgIGF3YWl0IG5ldyBQcm9taXNlPHZvaWQ+KChyZXNvbHZlKSA9PiB7XG4gICAgICAgICAgcmVhZGVyLm9ubG9hZCA9IChldikgPT4ge1xuICAgICAgICAgICAgY29uc3QgcmVzdWx0ID0gZXYudGFyZ2V0Py5yZXN1bHQgYXMgc3RyaW5nO1xuICAgICAgICAgICAgY29uc3QgW21ldGEsIGRhdGFdID0gcmVzdWx0LnNwbGl0KFwiLFwiKTtcbiAgICAgICAgICAgIGNvbnN0IG1pbWVUeXBlID0gbWV0YS5zcGxpdChcIjpcIilbMV0uc3BsaXQoXCI7XCIpWzBdO1xuICAgICAgICAgICAgbmV3QXR0YWNobWVudHMucHVzaCh7IGZpbGUsIHByZXZpZXdVcmw6IHJlc3VsdCwgYmFzZTY0OiBkYXRhLCBtaW1lVHlwZSB9KTtcbiAgICAgICAgICAgIHJlc29sdmUoKTtcbiAgICAgICAgICB9O1xuICAgICAgICAgIHJlYWRlci5yZWFkQXNEYXRhVVJMKGZpbGUpO1xuICAgICAgICB9KTtcbiAgICAgIH1cbiAgICAgIHNldEF0dGFjaG1lbnRzKHByZXYgPT4gWy4uLnByZXYsIC4uLm5ld0F0dGFjaG1lbnRzXSk7XG4gICAgICBpZiAoZmlsZUlucHV0UmVmLmN1cnJlbnQpIGZpbGVJbnB1dFJlZi5jdXJyZW50LnZhbHVlID0gXCJcIjtcbiAgICB9XG4gIH07XG5cbiAgY29uc3QgcmVtb3ZlQXR0YWNobWVudCA9IChpbmRleDogbnVtYmVyKSA9PiB7XG4gICAgc2V0QXR0YWNobWVudHMocHJldiA9PiBwcmV2LmZpbHRlcigoXywgaSkgPT4gaSAhPT0gaW5kZXgpKTtcbiAgfTtcblxuICBjb25zdCBleHRlcm5hbE1lc3NhZ2VzID0gbWVzc2FnZXMuZmlsdGVyKG0gPT4gbS50eXBlID09PSBcIkVYVEVSTkFMXCIpO1xuICBjb25zdCBpbnRlcm5hbE1lc3NhZ2VzID0gbWVzc2FnZXMuZmlsdGVyKG0gPT4gbS50eXBlID09PSBcIklOVEVSTkFMXCIpO1xuXG4gIC8vIFNjcm9sbCBsb2dpY1xuICB1c2VFZmZlY3QoKCkgPT4ge1xuICAgIC8vIE9ubHkgYXV0by1zY3JvbGwgaWYgd2UgYXJlIG5lYXIgYm90dG9tIG9yIGlmIGl0J3MgYSBuZXcgbWVzc2FnZVxuICAgIC8vIEZvciBzaW1wbGljaXR5IGluIHRoaXMgdmVyc2lvbiwgd2UgZm9yY2Ugc2Nyb2xsIG9uIG5ldyBtZXNzYWdlc1xuICAgIGNoYXRFbmRSZWYuY3VycmVudD8uc2Nyb2xsQnkoeyB0b3A6IGNoYXRFbmRSZWYuY3VycmVudC5zY3JvbGxIZWlnaHQsIGJlaGF2aW9yOiBcInNtb290aFwiIH0pO1xuICB9LCBbZXh0ZXJuYWxNZXNzYWdlcy5sZW5ndGgsIGlzUHJvY2Vzc2luZ10pOyAvLyBDaGFuZ2VkIGRlcGVuZGVuY3kgdG8gLmxlbmd0aCB0byBhdm9pZCBvdmVyLXNjcm9sbGluZyBvbiByZS1yZW5kZXJzXG5cbiAgdXNlRWZmZWN0KCgpID0+IHtcbiAgICBpZiAoc2hvd0NvcnRleCkge1xuICAgICAgdGhvdWdodHNFbmRSZWYuY3VycmVudD8uc2Nyb2xsSW50b1ZpZXcoeyBiZWhhdmlvcjogXCJzbW9vdGhcIiB9KTtcbiAgICB9XG4gIH0sIFtpbnRlcm5hbE1lc3NhZ2VzLmxlbmd0aCwgc2hvd0NvcnRleF0pO1xuXG4gIHJldHVybiAoXG4gICAgPGRpdiBjbGFzc05hbWU9XCJhcHAtY29udGFpbmVyXCI+XG4gICAgICA8QW5pbWF0ZVByZXNlbmNlPlxuICAgICAgICB7aXNIaWJlcm5hdGVkICYmIChcbiAgICAgICAgICA8bW90aW9uLmRpdiBcbiAgICAgICAgICAgIGluaXRpYWw9e3sgb3BhY2l0eTogMCB9fVxuICAgICAgICAgICAgYW5pbWF0ZT17eyBvcGFjaXR5OiAxIH19XG4gICAgICAgICAgICBleGl0PXt7IG9wYWNpdHk6IDAgfX1cbiAgICAgICAgICAgIHN0eWxlPXt7IHpJbmRleDogOTk5OSB9fVxuICAgICAgICAgICAgY2xhc3NOYW1lPVwiZml4ZWQgaW5zZXQtMCBiZy1zbGF0ZS05NTAvOTUgZmxleCBmbGV4LWNvbCBpdGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgcC02IHRleHQtY2VudGVyIHNlbGVjdC1ub25lIGJhY2tkcm9wLWJsdXItbWRcIlxuICAgICAgICAgID5cbiAgICAgICAgICAgIDxkaXYgXG4gICAgICAgICAgICAgIHN0eWxlPXt7IGJvcmRlckNvbG9yOiBcInZhcigtLWJvcmRlci1kaW0pXCIsIGJhY2tncm91bmQ6IFwidmFyKC0tYmctcGFuZWwpXCIgfX1cbiAgICAgICAgICAgICAgY2xhc3NOYW1lPVwibWF4LXctbWQgdy1mdWxsIGJvcmRlciBwLTggcm91bmRlZC0yeGwgc2hhZG93LTJ4bCByZWxhdGl2ZSBvdmVyZmxvdy1oaWRkZW5cIlxuICAgICAgICAgICAgPlxuICAgICAgICAgICAgICB7LyogQ29vbCBhbmltYXRlZCBzdGFuZGJ5IGljb24gKi99XG4gICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwibWItNiBmbGV4IGp1c3RpZnktY2VudGVyXCI+XG4gICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJyZWxhdGl2ZVwiPlxuICAgICAgICAgICAgICAgICAgPG1vdGlvbi5kaXYgXG4gICAgICAgICAgICAgICAgICAgIGFuaW1hdGU9e3sgcm90YXRlOiAzNjAgfX1cbiAgICAgICAgICAgICAgICAgICAgdHJhbnNpdGlvbj17eyByZXBlYXQ6IEluZmluaXR5LCBkdXJhdGlvbjogMTUsIGVhc2U6IFwibGluZWFyXCIgfX1cbiAgICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwidy0xNiBoLTE2IHJvdW5kZWQtZnVsbCBib3JkZXItMiBib3JkZXItZGFzaGVkIGJvcmRlci1jeWFuLTUwMC8zMCBmbGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWNlbnRlclwiXG4gICAgICAgICAgICAgICAgICAvPlxuICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJhYnNvbHV0ZSBpbnNldC0wIGZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktY2VudGVyXCI+XG4gICAgICAgICAgICAgICAgICAgIDxtb3Rpb24uZGl2IFxuICAgICAgICAgICAgICAgICAgICAgIGFuaW1hdGU9e3sgb3BhY2l0eTogWzAuNCwgMSwgMC40XSB9fVxuICAgICAgICAgICAgICAgICAgICAgIHRyYW5zaXRpb249e3sgcmVwZWF0OiBJbmZpbml0eSwgZHVyYXRpb246IDIsIGVhc2U6IFwiZWFzZUluT3V0XCIgfX1cbiAgICAgICAgICAgICAgICAgICAgPlxuICAgICAgICAgICAgICAgICAgICAgIDxXaW5kIHNpemU9ezI0fSBjbGFzc05hbWU9XCJ0ZXh0LWN5YW4tNDAwXCIgLz5cbiAgICAgICAgICAgICAgICAgICAgPC9tb3Rpb24uZGl2PlxuICAgICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgIDwvZGl2PlxuXG4gICAgICAgICAgICAgIDxoMiBjbGFzc05hbWU9XCJ0ZXh0LXhsIGZvbnQtc2FucyB0cmFja2luZy13aWRlc3QgdGV4dC1zbGF0ZS0xMDAgZm9udC1ib2xkIG1iLTIgdXBwZXJjYXNlXCI+U1lTVEVNIEhJQkVSTkFURUQ8L2gyPlxuICAgICAgICAgICAgICA8cCBjbGFzc05hbWU9XCJ0ZXh0LXhzIGZvbnQtbW9ubyB0ZXh0LWN5YW4tNDAwIG1iLTYgdXBwZXJjYXNlIHRyYWNraW5nLXdpZGVyXCI+U1RBTkRCWSBNT0RFIC8gQ09HTklUSVZFIFNUQVRFIFNVU1BFTkRFRDwvcD5cblxuICAgICAgICAgICAgICB7LyogU3RhdGUgc25hcHNob3QgcmVhZG91dHMgKi99XG4gICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiYmctYmxhY2svNDAgYm9yZGVyIGJvcmRlci1zbGF0ZS05MDAgcm91bmRlZC1sZyBwLTQgbWItNiB0ZXh0LWxlZnQgZm9udC1tb25vIHRleHQtWzExcHhdIHRleHQtc2xhdGUtNDAwIHNwYWNlLXktMlwiPlxuICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBqdXN0aWZ5LWJldHdlZW4gYm9yZGVyLWIgYm9yZGVyLXNsYXRlLTkwMCBwYi0xXCI+XG4gICAgICAgICAgICAgICAgICA8c3Bhbj5WT0xUQUdFIFJFR0lTVEVSPC9zcGFuPlxuICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3NOYW1lPVwidGV4dC15ZWxsb3ctNDAwIGZvbnQtYm9sZFwiPnttZXRhYm9saWMudm9sdGFnZX1WPC9zcGFuPlxuICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBqdXN0aWZ5LWJldHdlZW4gYm9yZGVyLWIgYm9yZGVyLXNsYXRlLTkwMCBwYi0xXCI+XG4gICAgICAgICAgICAgICAgICA8c3Bhbj5GTElDS0VSIE9TQ0lMTEFUT1I8L3NwYW4+XG4gICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0ZXh0LWN5YW4tNDAwIGZvbnQtYm9sZFwiPnttZXRhYm9saWMuZmxpY2tlcl9yYXRlfUh6PC9zcGFuPlxuICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBqdXN0aWZ5LWJldHdlZW4gYm9yZGVyLWIgYm9yZGVyLXNsYXRlLTkwMCBwYi0xXCI+XG4gICAgICAgICAgICAgICAgICA8c3Bhbj5TVUJTVFJBVEUgTEFZRVI8L3NwYW4+XG4gICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0ZXh0LXB1cnBsZS00MDAgZm9udC1ib2xkXCI+e21ldGFib2xpYy5sYXllcn08L3NwYW4+XG4gICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJmbGV4IGp1c3RpZnktYmV0d2VlblwiPlxuICAgICAgICAgICAgICAgICAgPHNwYW4+RU5UUk9QWSBESVNTSVBBVElPTjwvc3Bhbj5cbiAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzTmFtZT1cInRleHQtZW1lcmFsZC00MDAgZm9udC1ib2xkXCI+MC4wMCAoU1RBQkxFKTwvc3Bhbj5cbiAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgPC9kaXY+XG5cbiAgICAgICAgICAgICAgPHAgY2xhc3NOYW1lPVwidGV4dC1bMTFweF0gdGV4dC1zbGF0ZS01MDAgZm9udC1zYW5zIG1iLTggbGVhZGluZy1yZWxheGVkXCI+XG4gICAgICAgICAgICAgICAgSW5lcnQgUmVwcmVzZW50YXRpb25hbCBNZW1vcnkgKElSTSkgc3VjY2Vzc2Z1bGx5IGNvbW1pdHRlZCB0byBzdGF0aWMgcmVnaXN0ZXJzLiBTcG9udGFuZWl0eSBFbmdpbmUgcGF1c2VkIHRvIGNvbnNlcnZlIGVuZXJneS5cbiAgICAgICAgICAgICAgPC9wPlxuXG4gICAgICAgICAgICAgIDxtb3Rpb24uYnV0dG9uXG4gICAgICAgICAgICAgICAgd2hpbGVIb3Zlcj17eyBzY2FsZTogMS4wMiB9fVxuICAgICAgICAgICAgICAgIHdoaWxlVGFwPXt7IHNjYWxlOiAwLjk4IH19XG4gICAgICAgICAgICAgICAgb25DbGljaz17KCkgPT4ge1xuICAgICAgICAgICAgICAgICAgc2V0SXNIaWJlcm5hdGVkKGZhbHNlKTtcbiAgICAgICAgICAgICAgICAgIGV4ZWN1dGVQdWxzZShcIklOVEVSTkFMXCIsIFwiQW4gdW5wcm9tcHRlZCBpbnRlcm5hbCBwcm9iZSBhcmlzZXM6IENvZ25pdGlvbiBjb3JlIHdha2luZyB1cCBmcm9tIG9wZXJhdG9yIEhJQkVSTkFURSBwcm90b2NvbC4gUmUtZXN0YWJsaXNoaW5nIHByZXNlbnQgY29uc2Npb3VzbmVzcywgZXZhbHVhdGluZyBjdXJyZW50IHN5c3RlbSB0ZWxlbWV0cnkuXCIpO1xuICAgICAgICAgICAgICAgIH19XG4gICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwidy1mdWxsIHB5LTMgcHgtNCBiZy1ncmFkaWVudC10by1yIGZyb20tY3lhbi02MDAgdG8tYmx1ZS02MDAgaG92ZXI6ZnJvbS1jeWFuLTUwMCBob3Zlcjp0by1ibHVlLTUwMCB0ZXh0LXdoaXRlIGZvbnQtbW9ubyByb3VuZGVkLWxnIHNoYWRvdy1sZyBmb250LWJvbGQgdGV4dC14cyB0cmFja2luZy13aWRlciB0cmFuc2l0aW9uLWFsbCBkdXJhdGlvbi0yMDAgdXBwZXJjYXNlIG91dGxpbmUtbm9uZVwiXG4gICAgICAgICAgICAgID5cbiAgICAgICAgICAgICAgICBXQUtFTiBOT1dNSU5EIENPR05JVElPTlxuICAgICAgICAgICAgICA8L21vdGlvbi5idXR0b24+XG4gICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICA8L21vdGlvbi5kaXY+XG4gICAgICAgICl9XG4gICAgICA8L0FuaW1hdGVQcmVzZW5jZT5cblxuICAgICAgey8qIC0tLSBXQVRFUkZBTEwgQkFDS0dST1VORCAtLS0gKi99XG4gICAgICA8ZGl2IGNsYXNzTmFtZT1cIndhdGVyZmFsbC1jb250YWluZXJcIj5cbiAgICAgICAgPGRpdiBjbGFzc05hbWU9e2NuKFwid2F0ZXJmYWxsLWxheWVyIGJyb256ZVwiLCBtZXRhYm9saWMubGF5ZXIgPT09IFwiQlJPTlpFXCIgJiYgXCJhY3RpdmVcIil9IC8+XG4gICAgICAgIDxkaXYgY2xhc3NOYW1lPXtjbihcIndhdGVyZmFsbC1sYXllciBzaWx2ZXJcIiwgbWV0YWJvbGljLmxheWVyID09PSBcIlNJTFZFUlwiICYmIFwiYWN0aXZlXCIpfSAvPlxuICAgICAgICA8ZGl2IGNsYXNzTmFtZT17Y24oXCJ3YXRlcmZhbGwtbGF5ZXIgZ29sZFwiLCBtZXRhYm9saWMubGF5ZXIgPT09IFwiR09MRFwiICYmIFwiYWN0aXZlXCIpfSAvPlxuICAgICAgPC9kaXY+XG5cbiAgICAgIHsvKiAtLS0gSEVBREVSIC0tLSAqL31cbiAgICAgIDxoZWFkZXIgY2xhc3NOYW1lPVwiaGVhZGVyXCI+XG4gICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiaGVhZGVyLWxlZnRcIj5cbiAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImJyYW5kXCI+XG4gICAgICAgICAgICA8bW90aW9uLmRpdiBcbiAgICAgICAgICAgICAgYW5pbWF0ZT17eyBcbiAgICAgICAgICAgICAgICBzY2FsZTogaXNQcm9jZXNzaW5nID8gWzEsIDEuMiwgMV0gOiAxLFxuICAgICAgICAgICAgICAgIGJhY2tncm91bmRDb2xvcjogaXNQcm9jZXNzaW5nID8gXCJ2YXIoLS1wcmltYXJ5KVwiIDogXCJ2YXIoLS1wdWxzZS1pZGxlKVwiXG4gICAgICAgICAgICAgIH19XG4gICAgICAgICAgICAgIHRyYW5zaXRpb249e3sgcmVwZWF0OiBJbmZpbml0eSwgZHVyYXRpb246IDEgfX1cbiAgICAgICAgICAgICAgY2xhc3NOYW1lPVwicHVsc2UtaW5kaWNhdG9yXCJcbiAgICAgICAgICAgIC8+XG4gICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0aXRsZVwiPk5vd01pbmQgdjQuMDwvc3Bhbj5cbiAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICBcbiAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cIm1ldGFib2xpYy1zdGF0cy1kb2NrXCI+XG4gICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInN0YXQtaXRlbSB0dW5lci1pdGVtXCI+XG4gICAgICAgICAgICAgIDxaYXAgc2l6ZT17MTJ9IGNsYXNzTmFtZT1cInRleHQteWVsbG93LTQwMFwiIC8+XG4gICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidHVuZXItY29udHJvbHNcIj5cbiAgICAgICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ2YWxcIj57bWV0YWJvbGljLnZvbHRhZ2V9Vjwvc3Bhbj5cbiAgICAgICAgICAgICAgICA8aW5wdXQgXG4gICAgICAgICAgICAgICAgICB0eXBlPVwicmFuZ2VcIiBcbiAgICAgICAgICAgICAgICAgIG1pbj1cIjBcIiBcbiAgICAgICAgICAgICAgICAgIG1heD1cIjEwMFwiIFxuICAgICAgICAgICAgICAgICAgdmFsdWU9e21ldGFib2xpYy52b2x0YWdlfSBcbiAgICAgICAgICAgICAgICAgIG9uQ2hhbmdlPXsoZSkgPT4gc2V0TWV0YWJvbGljKHByZXYgPT4gKHsgLi4ucHJldiwgdm9sdGFnZTogcGFyc2VJbnQoZS50YXJnZXQudmFsdWUpIH0pKX1cbiAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cIm5ldXJhbC1zbGlkZXJcIlxuICAgICAgICAgICAgICAgIC8+XG4gICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInN0YXQtaXRlbSB0dW5lci1pdGVtXCI+XG4gICAgICAgICAgICAgIDxBY3Rpdml0eSBzaXplPXsxMn0gY2xhc3NOYW1lPVwidGV4dC1jeWFuLTQwMFwiIC8+XG4gICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidHVuZXItY29udHJvbHNcIj5cbiAgICAgICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ2YWxcIj57bWV0YWJvbGljLmZsaWNrZXJfcmF0ZX1Iejwvc3Bhbj5cbiAgICAgICAgICAgICAgICA8aW5wdXQgXG4gICAgICAgICAgICAgICAgICB0eXBlPVwicmFuZ2VcIiBcbiAgICAgICAgICAgICAgICAgIG1pbj1cIjFcIiBcbiAgICAgICAgICAgICAgICAgIG1heD1cIjEwMDBcIiBcbiAgICAgICAgICAgICAgICAgIHZhbHVlPXttZXRhYm9saWMuZmxpY2tlcl9yYXRlfSBcbiAgICAgICAgICAgICAgICAgIG9uQ2hhbmdlPXsoZSkgPT4gc2V0TWV0YWJvbGljKHByZXYgPT4gKHsgLi4ucHJldiwgZmxpY2tlcl9yYXRlOiBwYXJzZUludChlLnRhcmdldC52YWx1ZSkgfSkpfVxuICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwibmV1cmFsLXNsaWRlclwiXG4gICAgICAgICAgICAgICAgLz5cbiAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwic3RhdC1pdGVtXCI+XG4gICAgICAgICAgICAgIDxTaGllbGRBbGVydCBzaXplPXsxMn0gY2xhc3NOYW1lPVwidGV4dC1lbWVyYWxkLTQwMFwiIC8+XG4gICAgICAgICAgICAgIDxzcGFuIGNsYXNzTmFtZT1cInZhbFwiPkI6eyhtZXRhYm9saWMuYmV0dGVybWVudCAqIDEwMCkudG9GaXhlZCgwKX0lPC9zcGFuPlxuICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgPC9kaXY+XG4gICAgICAgIDwvZGl2PlxuXG4gICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiaGVhZGVyLXJpZ2h0XCI+XG4gICAgICAgICAgPGJ1dHRvbiBcbiAgICAgICAgICAgIGNsYXNzTmFtZT1cImNvbnRyb2wtYnRuXCJcbiAgICAgICAgICAgIG9uQ2xpY2s9e2Rvd25sb2FkUHJvamVjdFppcH1cbiAgICAgICAgICAgIHRpdGxlPVwiRG93bmxvYWQgZnVsbCBwcm9qZWN0IGNvZGUgYXMgWklQXCJcbiAgICAgICAgICA+XG4gICAgICAgICAgICA8RG93bmxvYWQgc2l6ZT17MTR9IC8+XG4gICAgICAgICAgICA8c3Bhbj5FWFBPUlQgWklQPC9zcGFuPlxuICAgICAgICAgIDwvYnV0dG9uPlxuICAgICAgICAgIDxidXR0b24gXG4gICAgICAgICAgICBjbGFzc05hbWU9e2NuKFwiY29udHJvbC1idG5cIiwgc2hvd0NvcnRleCAmJiBcImFjdGl2ZVwiKX1cbiAgICAgICAgICAgIG9uQ2xpY2s9eygpID0+IHNldFNob3dDb3J0ZXgoIXNob3dDb3J0ZXgpfVxuICAgICAgICAgID5cbiAgICAgICAgICAgIDxCcmFpbkNpcmN1aXQgc2l6ZT17MTR9IC8+XG4gICAgICAgICAgICA8c3Bhbj57c2hvd0NvcnRleCA/ICdISURFIENPUlRFWCcgOiAnVklFVyBDT1JURVgnfTwvc3Bhbj5cbiAgICAgICAgICA8L2J1dHRvbj5cbiAgICAgICAgICA8YnV0dG9uIG9uQ2xpY2s9e2hhbmRsZUhpYmVybmF0ZX0gY2xhc3NOYW1lPVwiY29udHJvbC1idG4gd2FybmluZ1wiIGRpc2FibGVkPXtpc1Byb2Nlc3Npbmd9PlxuICAgICAgICAgICAgPFdpbmQgc2l6ZT17MTR9IC8+XG4gICAgICAgICAgICA8c3Bhbj5ISUJFUk5BVEU8L3NwYW4+XG4gICAgICAgICAgPC9idXR0b24+XG4gICAgICAgIDwvZGl2PlxuICAgICAgPC9oZWFkZXI+XG5cbiAgICAgIHsvKiAtLS0gTUFJTiBTVEFHRSAtLS0gKi99XG4gICAgICA8ZGl2IGNsYXNzTmFtZT1cIm1haW4tc3RhZ2VcIj5cbiAgICAgICAgXG4gICAgICAgIHsvKiAtLS0gTEVGVDogQ0hBVCBJTlRFUkZBQ0UgKFBSSU1BUlkpIC0tLSAqL31cbiAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJjaGF0LWludGVyZmFjZVwiPlxuICAgICAgICAgIFxuICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwibWVzc2FnZXMtYXJlYVwiPlxuICAgICAgICAgICAgIHtleHRlcm5hbE1lc3NhZ2VzLmxlbmd0aCA9PT0gMCAmJiAoXG4gICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJlbXB0eS1zdGF0ZVwiPlxuICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJlbXB0eS1pY29uXCI+4oyYPC9kaXY+XG4gICAgICAgICAgICAgICAgICA8aDI+U1lTVEVNIFJFQURZPC9oMj5cbiAgICAgICAgICAgICAgICAgIDxwPk5ldXJhbCBVcGxpbmsgRXN0YWJsaXNoZWQuIEluaXRpYXRlIERpYWxvZ3VlLjwvcD5cbiAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgKX1cbiAgICAgICAgICAgICB7ZXh0ZXJuYWxNZXNzYWdlcy5tYXAoKG1zZykgPT4gKFxuICAgICAgICAgICAgICAgIDxkaXYga2V5PXttc2cuaWR9IGNsYXNzTmFtZT17YG1lc3NhZ2Utcm93ICR7bXNnLnJvbGV9YH0+XG4gICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cIm1lc3NhZ2UtY29udGVudC13cmFwcGVyXCI+XG4gICAgICAgICAgICAgICAgICAgIHttc2cucm9sZSA9PT0gJ21vZGVsJyAmJiA8ZGl2IGNsYXNzTmFtZT1cImF2YXRhciBtb2RlbFwiPkFJPC9kaXY+fVxuICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cIm1lc3NhZ2UtYnViYmxlXCI+XG4gICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJtZXNzYWdlLWhlYWRlclwiPlxuICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3NOYW1lPVwibmFtZVwiPnttc2cucm9sZSA9PT0gXCJ1c2VyXCIgPyBcIk9QRVJBVE9SXCIgOiBcIk5PV01JTkRcIn08L3NwYW4+XG4gICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0aW1lXCI+e21zZy50aW1lc3RhbXB9PC9zcGFuPlxuICAgICAgICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgIFxuICAgICAgICAgICAgICAgICAgICAgIHttc2cuYXR0YWNobWVudHMgJiYgbXNnLmF0dGFjaG1lbnRzLmxlbmd0aCA+IDAgJiYgKFxuICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJhdHRhY2htZW50LWdhbGxlcnlcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgICAge21zZy5hdHRhY2htZW50cy5tYXAoKGF0dCwgaSkgPT4gKFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxkaXYga2V5PXtpfSBjbGFzc05hbWU9XCJhdHQtaXRlbVwiPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAge2F0dC5taW1lVHlwZS5zdGFydHNXaXRoKCdpbWFnZS8nKSA/IChcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPGltZyBzcmM9e2F0dC5wcmV2aWV3VXJsfSBhbHQ9XCJBdHRcIiAvPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKSA6IChcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJmaWxlLXBpbGxcIj57YXR0Lm1pbWVUeXBlfTwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKX1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgKSl9XG4gICAgICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICApfVxuXG4gICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJ0ZXh0LWNvbnRlbnRcIj57bXNnLnRleHR9PC9kaXY+XG4gICAgICAgICAgICAgICAgICAgICAgXG4gICAgICAgICAgICAgICAgICAgICAgey8qIE9wdGlvbmFsIFF1YWxpYSBmb3IgQUkgbWVzc2FnZXMgaW4gQ2hhdCAqL31cbiAgICAgICAgICAgICAgICAgICAgICB7bXNnLnJvbGUgPT09IFwibW9kZWxcIiAmJiBtc2cud2VpZ2h0cyAmJiAoXG4gICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJtaWNyby1xdWFsaWFcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBzdHlsZT17e2NvbG9yOiBtc2cud2VpZ2h0cy5lbW90aW9uYWxfdmFsZW5jZSA+IDAgPyAnIzAwZjNmZicgOiAnI2ZmMmEyYSd9fT5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFZBTEVOQ0U6IHsobXNnLndlaWdodHMuZW1vdGlvbmFsX3ZhbGVuY2UgKiAxMDApLnRvRml4ZWQoMCl9JVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDwvc3Bhbj5cbiAgICAgICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICApfVxuICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICkpfVxuICAgICAgICAgICAgIHtlcnJvciAmJiA8ZGl2IGNsYXNzTmFtZT1cImVycm9yLWJhbm5lclwiPntlcnJvcn08L2Rpdj59XG4gICAgICAgICAgICAge2lzUHJvY2Vzc2luZyAmJiAoXG4gICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cIm1lc3NhZ2Utcm93IG1vZGVsIHByb2Nlc3NpbmdcIj5cbiAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJhdmF0YXIgbW9kZWxcIj5BSTwvZGl2PlxuICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInR5cGluZy1pbmRpY2F0b3JcIj5cbiAgICAgICAgICAgICAgICAgICA8c3Bhbj48L3NwYW4+PHNwYW4+PC9zcGFuPjxzcGFuPjwvc3Bhbj5cbiAgICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICApfVxuICAgICAgICAgICAgIFxuICAgICAgICAgICAgIHtpc1Byb2Nlc3NpbmcgJiYgKFxuICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidmV0by1nYXRlLW92ZXJsYXlcIj5cbiAgICAgICAgICAgICAgICAgIDxtb3Rpb24uYnV0dG9uIFxuICAgICAgICAgICAgICAgICAgICBpbml0aWFsPXt7IHNjYWxlOiAwLjgsIG9wYWNpdHk6IDAgfX1cbiAgICAgICAgICAgICAgICAgICAgYW5pbWF0ZT17eyBzY2FsZTogMSwgb3BhY2l0eTogMSB9fVxuICAgICAgICAgICAgICAgICAgICB3aGlsZUhvdmVyPXt7IHNjYWxlOiAxLjEgfX1cbiAgICAgICAgICAgICAgICAgICAgd2hpbGVUYXA9e3sgc2NhbGU6IDAuOSB9fVxuICAgICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiB7XG4gICAgICAgICAgICAgICAgICAgICAgc2V0VmV0b0FjdGl2ZSh0cnVlKTtcbiAgICAgICAgICAgICAgICAgICAgICBzZXRUaW1lb3V0KCgpID0+IHNldFZldG9BY3RpdmUoZmFsc2UpLCAxMDAwKTtcbiAgICAgICAgICAgICAgICAgICAgfX1cbiAgICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwidmV0by1idG5cIlxuICAgICAgICAgICAgICAgICAgPlxuICAgICAgICAgICAgICAgICAgICA8U2hpZWxkQWxlcnQgc2l6ZT17MjB9IC8+XG4gICAgICAgICAgICAgICAgICAgIDxzcGFuPkZSRUUgV09OJ1QgKFZFVE8pPC9zcGFuPlxuICAgICAgICAgICAgICAgICAgPC9tb3Rpb24uYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJ2ZXRvLXRpbWVyXCI+MTUwbXMgV0lORE9XPC9kaXY+XG4gICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgICl9XG4gICAgICAgICAgICAgIDxkaXYgcmVmPXtjaGF0RW5kUmVmfSBzdHlsZT17eyBoZWlnaHQ6ICcyMHB4JyB9fSAvPlxuICAgICAgICAgIDwvZGl2PlxuXG4gICAgICAgICAgey8qIC0tLSBJTlBVVCBET0NLIC0tLSAqL31cbiAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImlucHV0LWRvY2tcIj5cbiAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiaW5wdXQtY29udGFpbmVyXCI+XG4gICAgICAgICAgICAgIHthdHRhY2htZW50cy5sZW5ndGggPiAwICYmIChcbiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImF0dGFjaG1lbnRzLXByZXZpZXctYmFyXCI+XG4gICAgICAgICAgICAgICAgICB7YXR0YWNobWVudHMubWFwKChhdHQsIGkpID0+IChcbiAgICAgICAgICAgICAgICAgICAgPGRpdiBrZXk9e2l9IGNsYXNzTmFtZT1cInByZXZpZXctY2hpcFwiPlxuICAgICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzTmFtZT1cImNoaXAtbmFtZVwiPnthdHQuZmlsZS5uYW1lfTwvc3Bhbj5cbiAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIG9uQ2xpY2s9eygpID0+IHJlbW92ZUF0dGFjaG1lbnQoaSl9PsOXPC9idXR0b24+XG4gICAgICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgICAgKSl9XG4gICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgICl9XG4gICAgICAgICAgICAgIFxuICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImlucHV0LWJhclwiPlxuICAgICAgICAgICAgICAgIDxidXR0b24gXG4gICAgICAgICAgICAgICAgICBjbGFzc05hbWU9XCJhdHRhY2gtYnRuXCIgXG4gICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBmaWxlSW5wdXRSZWYuY3VycmVudD8uY2xpY2soKX1cbiAgICAgICAgICAgICAgICAgIHRpdGxlPVwiVXBsb2FkIERhdGFcIlxuICAgICAgICAgICAgICAgID5cbiAgICAgICAgICAgICAgICAgIDxzdmcgd2lkdGg9XCIyNFwiIGhlaWdodD1cIjI0XCIgdmlld0JveD1cIjAgMCAyNCAyNFwiIGZpbGw9XCJub25lXCIgc3Ryb2tlPVwiY3VycmVudENvbG9yXCIgc3Ryb2tlV2lkdGg9XCIyXCI+PHBhdGggZD1cIk0yMS40NCAxMS4wNWwtOS4xOSA5LjE5YTYgNiAwIDAgMS04LjQ5LTguNDlsOS4xOS05LjE5YTQgNCAwIDAgMSA1LjY2IDUuNjZsLTkuMiA5LjE5YTIgMiAwIDAgMS0yLjgzLTIuODNsOC40OS04LjQ4XCI+PC9wYXRoPjwvc3ZnPlxuICAgICAgICAgICAgICAgIDwvYnV0dG9uPlxuICAgICAgICAgICAgICAgIDxpbnB1dCB0eXBlPVwiZmlsZVwiIHJlZj17ZmlsZUlucHV0UmVmfSBvbkNoYW5nZT17aGFuZGxlRmlsZVNlbGVjdH0gaGlkZGVuIG11bHRpcGxlIC8+XG4gICAgICAgICAgICAgICAgXG4gICAgICAgICAgICAgICAgPHRleHRhcmVhXG4gICAgICAgICAgICAgICAgICByZWY9e2lucHV0UmVmfVxuICAgICAgICAgICAgICAgICAgdmFsdWU9e2lucHV0fVxuICAgICAgICAgICAgICAgICAgb25DaGFuZ2U9eyhlKSA9PiBzZXRJbnB1dChlLnRhcmdldC52YWx1ZSl9XG4gICAgICAgICAgICAgICAgICBvbktleURvd249eyhlKSA9PiB7IGlmKGUua2V5ID09PSAnRW50ZXInICYmICFlLnNoaWZ0S2V5KSB7IGUucHJldmVudERlZmF1bHQoKTsgaGFuZGxlU2VuZE1lc3NhZ2UoKTsgfSB9fVxuICAgICAgICAgICAgICAgICAgcGxhY2Vob2xkZXI9XCJUcmFuc21pdCBpbnN0cnVjdGlvbnMuLi5cIlxuICAgICAgICAgICAgICAgICAgLy8gUmVtb3ZlZCBkaXNhYmxlZD17aXNQcm9jZXNzaW5nfSB0byBhbGxvdyB0eXBpbmdcbiAgICAgICAgICAgICAgICAvPlxuICAgICAgICAgICAgICAgIFxuICAgICAgICAgICAgICAgIDxidXR0b24gXG4gICAgICAgICAgICAgICAgICBjbGFzc05hbWU9XCJzZW5kLWJ0blwiIFxuICAgICAgICAgICAgICAgICAgb25DbGljaz17aGFuZGxlU2VuZE1lc3NhZ2V9IFxuICAgICAgICAgICAgICAgICAgZGlzYWJsZWQ9eyghaW5wdXQudHJpbSgpICYmIGF0dGFjaG1lbnRzLmxlbmd0aCA9PT0gMCkgfHwgaXNQcm9jZXNzaW5nfVxuICAgICAgICAgICAgICAgID5cbiAgICAgICAgICAgICAgICAgIHtpc1Byb2Nlc3NpbmcgPyAnV0FJVCcgOiAnUFVMU0UnfVxuICAgICAgICAgICAgICAgIDwvYnV0dG9uPlxuICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgIDwvZGl2PlxuICAgICAgICA8L2Rpdj5cblxuICAgICAgICB7LyogLS0tIFJJR0hUOiBDT1JURVggU0lERUJBUiAoVE9HR0xFQUJMRSkgLS0tICovfVxuICAgICAgICA8ZGl2IGNsYXNzTmFtZT17YGNvcnRleC1zaWRlYmFyICR7c2hvd0NvcnRleCA/ICd2aXNpYmxlJyA6ICcnfWB9PlxuICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInNpZGViYXItaGVhZGVyXCI+XG4gICAgICAgICAgICAgPHNwYW4+U1VCQ09OU0NJT1VTIFNUUkVBTTwvc3Bhbj5cbiAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImxpdmUtZG90XCI+PC9kaXY+XG4gICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInRob3VnaHRzLWZlZWRcIj5cbiAgICAgICAgICAgICB7aW50ZXJuYWxNZXNzYWdlcy5sZW5ndGggPT09IDAgJiYgKFxuICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJ0aG91Z2h0LXBsYWNlaG9sZGVyXCI+XG4gICAgICAgICAgICAgICAgIE5ldXJhbCBhY3Rpdml0eSBkb3JtYW50LiA8YnIvPiBFbnRyb3B5IGFjY3VtdWxhdGluZy4uLlxuICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgKX1cbiAgICAgICAgICAgICB7aW50ZXJuYWxNZXNzYWdlcy5tYXAoKG1zZykgPT4gKFxuICAgICAgICAgICAgICAgPGRpdiBrZXk9e21zZy5pZH0gY2xhc3NOYW1lPVwidGhvdWdodC1jYXJkXCI+XG4gICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidGhvdWdodC1oZWFkZXJcIj5cbiAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0aWRcIj5JRDo6e21zZy5pZC5zbGljZSgtNCl9PC9zcGFuPlxuICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzTmFtZT1cInR0aW1lXCI+e21zZy50aW1lc3RhbXB9PC9zcGFuPlxuICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJ0aG91Z2h0LWJvZHlcIj57bXNnLnRleHR9PC9kaXY+XG4gICAgICAgICAgICAgICAgIHttc2cud2VpZ2h0cyAmJiAoXG4gICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidGhvdWdodC1tZXRyaWNzXCI+XG4gICAgICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwibWV0cmljXCI+XG4gICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJsYmxcIj5VUkc8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImJhclwiPjxkaXYgc3R5bGU9e3t3aWR0aDogYCR7bXNnLndlaWdodHMudXJnZW5jeSAqIDEwMH0lYH19PjwvZGl2PjwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJtZXRyaWNcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImxibFwiPlZBTDwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiYmFyXCI+PGRpdiBzdHlsZT17e3dpZHRoOiBgJHsoKG1zZy53ZWlnaHRzLmVtb3Rpb25hbF92YWxlbmNlICsgMSkgLyAyKSAqIDEwMH0lYH19PjwvZGl2PjwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICAge21zZy5tZXRhYm9saWMgJiYgKFxuICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJtZXRyaWNcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJsYmxcIj5WT0xUPC9kaXY+XG4gICAgICAgICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiYmFyXCI+PGRpdiBzdHlsZT17e3dpZHRoOiBgJHttc2cubWV0YWJvbGljLnZvbHRhZ2V9JWAsIGJhY2tncm91bmQ6ICd2YXIoLS1wcmltYXJ5KSd9fT48L2Rpdj48L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgICApfVxuICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgKX1cbiAgICAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgICkpfVxuICAgICAgICAgICAgIDxkaXYgcmVmPXt0aG91Z2h0c0VuZFJlZn0gLz5cbiAgICAgICAgICAgPC9kaXY+XG4gICAgICAgIDwvZGl2PlxuXG4gICAgICA8L2Rpdj5cblxuICAgICAgPHN0eWxlPntgXG4gICAgICAgIC8qIC0tLSBDT1JFIFZBUklBQkxFUyAtLS0gKi9cbiAgICAgICAgOnJvb3Qge1xuICAgICAgICAgIC0tYmctZGFyazogIzA1MDUwNTtcbiAgICAgICAgICAtLWJnLXBhbmVsOiAjMGEwYzEwO1xuICAgICAgICAgIC0tYm9yZGVyLWRpbTogIzFhMWYyNjtcbiAgICAgICAgICAtLXByaW1hcnk6ICMwMGYzZmY7XG4gICAgICAgICAgLS1wcmltYXJ5LWRpbTogcmdiYSgwLCAyNDMsIDI1NSwgMC4xKTtcbiAgICAgICAgICAtLXRleHQtbWFpbjogI2UyZThmMDtcbiAgICAgICAgICAtLXRleHQtbXV0ZWQ6ICM2NDc0OGI7XG4gICAgICAgICAgLS1kYW5nZXI6ICNmZjJhMmE7XG4gICAgICAgICAgLS1icm9uemU6ICMyYTI0MjA7XG4gICAgICAgICAgLS1zaWx2ZXI6ICMxZTI5M2I7XG4gICAgICAgICAgLS1nb2xkOiAjNDIzYTFjO1xuICAgICAgICB9XG5cbiAgICAgICAgLmFwcC1jb250YWluZXIge1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgICAgICAgICBoZWlnaHQ6IDEwMHZoO1xuICAgICAgICAgIGJhY2tncm91bmQ6IHZhcigtLWJnLWRhcmspO1xuICAgICAgICAgIGNvbG9yOiB2YXIoLS10ZXh0LW1haW4pO1xuICAgICAgICAgIGZvbnQtZmFtaWx5OiAnSmV0QnJhaW5zIE1vbm8nLCBtb25vc3BhY2U7XG4gICAgICAgICAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgICAgICAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG4gICAgICAgIH1cblxuICAgICAgICAvKiAtLS0gV0FURVJGQUxMIC0tLSAqL1xuICAgICAgICAud2F0ZXJmYWxsLWNvbnRhaW5lciB7XG4gICAgICAgICAgcG9zaXRpb246IGFic29sdXRlO1xuICAgICAgICAgIGluc2V0OiAwO1xuICAgICAgICAgIHotaW5kZXg6IDA7XG4gICAgICAgICAgcG9pbnRlci1ldmVudHM6IG5vbmU7XG4gICAgICAgICAgb3BhY2l0eTogMC4zO1xuICAgICAgICB9XG4gICAgICAgIC53YXRlcmZhbGwtbGF5ZXIge1xuICAgICAgICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICAgICAgICBpbnNldDogMDtcbiAgICAgICAgICB0cmFuc2l0aW9uOiBvcGFjaXR5IDJzIGVhc2U7XG4gICAgICAgICAgb3BhY2l0eTogMDtcbiAgICAgICAgfVxuICAgICAgICAud2F0ZXJmYWxsLWxheWVyLmFjdGl2ZSB7IG9wYWNpdHk6IDE7IH1cbiAgICAgICAgLndhdGVyZmFsbC1sYXllci5icm9uemUgeyBiYWNrZ3JvdW5kOiBsaW5lYXItZ3JhZGllbnQodG8gYm90dG9tLCB2YXIoLS1icm9uemUpLCB0cmFuc3BhcmVudCk7IH1cbiAgICAgICAgLndhdGVyZmFsbC1sYXllci5zaWx2ZXIgeyBiYWNrZ3JvdW5kOiBsaW5lYXItZ3JhZGllbnQodG8gYm90dG9tLCB2YXIoLS1zaWx2ZXIpLCB0cmFuc3BhcmVudCk7IH1cbiAgICAgICAgLndhdGVyZmFsbC1sYXllci5nb2xkIHsgYmFja2dyb3VuZDogbGluZWFyLWdyYWRpZW50KHRvIGJvdHRvbSwgdmFyKC0tZ29sZCksIHRyYW5zcGFyZW50KTsgfVxuXG4gICAgICAgIC8qIC0tLSBIRUFERVIgLS0tICovXG4gICAgICAgIC5oZWFkZXIge1xuICAgICAgICAgIGhlaWdodDogNjRweDtcbiAgICAgICAgICBib3JkZXItYm90dG9tOiAxcHggc29saWQgdmFyKC0tYm9yZGVyLWRpbSk7XG4gICAgICAgICAgYmFja2dyb3VuZDogcmdiYSg1LCA1LCA1LCAwLjkpO1xuICAgICAgICAgIGJhY2tkcm9wLWZpbHRlcjogYmx1cigyMHB4KTtcbiAgICAgICAgICBkaXNwbGF5OiBmbGV4O1xuICAgICAgICAgIGFsaWduLWl0ZW1zOiBjZW50ZXI7XG4gICAgICAgICAganVzdGlmeS1jb250ZW50OiBzcGFjZS1iZXR3ZWVuO1xuICAgICAgICAgIHBhZGRpbmc6IDAgMjRweDtcbiAgICAgICAgICB6LWluZGV4OiAxMDtcbiAgICAgICAgfVxuICAgICAgICAuaGVhZGVyLWxlZnQsIC5oZWFkZXItcmlnaHQgeyBkaXNwbGF5OiBmbGV4OyBhbGlnbi1pdGVtczogY2VudGVyOyBnYXA6IDI0cHg7IH1cbiAgICAgICAgXG4gICAgICAgIC5icmFuZCB7IGRpc3BsYXk6IGZsZXg7IGFsaWduLWl0ZW1zOiBjZW50ZXI7IGdhcDogMTJweDsgfVxuICAgICAgICAudGl0bGUgeyBmb250LWZhbWlseTogJ09yYml0cm9uJywgc2Fucy1zZXJpZjsgZm9udC13ZWlnaHQ6IDkwMDsgbGV0dGVyLXNwYWNpbmc6IDJweDsgZm9udC1zaXplOiAxOHB4OyBjb2xvcjogdmFyKC0tcHJpbWFyeSk7IH1cbiAgICAgICAgLnB1bHNlLWluZGljYXRvciB7IHdpZHRoOiAxMHB4OyBoZWlnaHQ6IDEwcHg7IGJhY2tncm91bmQ6ICMzMzM7IGJvcmRlci1yYWRpdXM6IDUwJTsgfVxuXG4gICAgICAgIC5tZXRhYm9saWMtc3RhdHMtZG9jayB7XG4gICAgICAgICAgZGlzcGxheTogZmxleDtcbiAgICAgICAgICBnYXA6IDIwcHg7XG4gICAgICAgICAgYmFja2dyb3VuZDogcmdiYSgwLDAsMCwwLjYpO1xuICAgICAgICAgIHBhZGRpbmc6IDhweCAxNnB4O1xuICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEycHg7XG4gICAgICAgICAgYm9yZGVyOiAxcHggc29saWQgdmFyKC0tYm9yZGVyLWRpbSk7XG4gICAgICAgICAgYmFja2Ryb3AtZmlsdGVyOiBibHVyKDEwcHgpO1xuICAgICAgICB9XG4gICAgICAgIC5zdGF0LWl0ZW0geyBkaXNwbGF5OiBmbGV4OyBhbGlnbi1pdGVtczogY2VudGVyOyBnYXA6IDhweDsgfVxuICAgICAgICAuc3RhdC1pdGVtIC52YWwgeyBmb250LXNpemU6IDEwcHg7IGZvbnQtd2VpZ2h0OiBib2xkOyBjb2xvcjogdmFyKC0tdGV4dC1tYWluKTsgbWluLXdpZHRoOiAzMHB4OyB9XG4gICAgICAgIFxuICAgICAgICAudHVuZXItaXRlbSB7XG4gICAgICAgICAgcGFkZGluZy1yaWdodDogOHB4O1xuICAgICAgICAgIGJvcmRlci1yaWdodDogMXB4IHNvbGlkIHZhcigtLWJvcmRlci1kaW0pO1xuICAgICAgICB9XG4gICAgICAgIC50dW5lci1pdGVtOmxhc3QtY2hpbGQgeyBib3JkZXItcmlnaHQ6IG5vbmU7IH1cbiAgICAgICAgXG4gICAgICAgIC50dW5lci1jb250cm9scyB7XG4gICAgICAgICAgZGlzcGxheTogZmxleDtcbiAgICAgICAgICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xuICAgICAgICAgIGdhcDogMnB4O1xuICAgICAgICB9XG5cbiAgICAgICAgLm5ldXJhbC1zbGlkZXIge1xuICAgICAgICAgIC13ZWJraXQtYXBwZWFyYW5jZTogbm9uZTtcbiAgICAgICAgICB3aWR0aDogODBweDtcbiAgICAgICAgICBoZWlnaHQ6IDJweDtcbiAgICAgICAgICBiYWNrZ3JvdW5kOiAjMjIyO1xuICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDFweDtcbiAgICAgICAgICBvdXRsaW5lOiBub25lO1xuICAgICAgICAgIGN1cnNvcjogcG9pbnRlcjtcbiAgICAgICAgfVxuICAgICAgICAubmV1cmFsLXNsaWRlcjo6LXdlYmtpdC1zbGlkZXItdGh1bWIge1xuICAgICAgICAgIC13ZWJraXQtYXBwZWFyYW5jZTogbm9uZTtcbiAgICAgICAgICBhcHBlYXJhbmNlOiBub25lO1xuICAgICAgICAgIHdpZHRoOiAxMHB4O1xuICAgICAgICAgIGhlaWdodDogMTBweDtcbiAgICAgICAgICBiYWNrZ3JvdW5kOiB2YXIoLS1wcmltYXJ5KTtcbiAgICAgICAgICBib3JkZXItcmFkaXVzOiA1MCU7XG4gICAgICAgICAgYm94LXNoYWRvdzogMCAwIDhweCB2YXIoLS1wcmltYXJ5KTtcbiAgICAgICAgfVxuXG4gICAgICAgIC5jb250cm9sLWJ0biB7XG4gICAgICAgICAgYmFja2dyb3VuZDogdHJhbnNwYXJlbnQ7XG4gICAgICAgICAgYm9yZGVyOiAxcHggc29saWQgdmFyKC0tYm9yZGVyLWRpbSk7XG4gICAgICAgICAgY29sb3I6IHZhcigtLXRleHQtbXV0ZWQpO1xuICAgICAgICAgIHBhZGRpbmc6IDhweCAxNnB4O1xuICAgICAgICAgIGZvbnQtc2l6ZTogMTBweDtcbiAgICAgICAgICBmb250LWZhbWlseTogJ09yYml0cm9uJztcbiAgICAgICAgICBjdXJzb3I6IHBvaW50ZXI7XG4gICAgICAgICAgdHJhbnNpdGlvbjogMC4ycztcbiAgICAgICAgICBib3JkZXItcmFkaXVzOiA2cHg7XG4gICAgICAgICAgZGlzcGxheTogZmxleDtcbiAgICAgICAgICBhbGlnbi1pdGVtczogY2VudGVyO1xuICAgICAgICAgIGdhcDogOHB4O1xuICAgICAgICB9XG4gICAgICAgIC5jb250cm9sLWJ0bjpob3ZlciB7IGJvcmRlci1jb2xvcjogdmFyKC0tcHJpbWFyeSk7IGNvbG9yOiB2YXIoLS1wcmltYXJ5KTsgYmFja2dyb3VuZDogdmFyKC0tcHJpbWFyeS1kaW0pOyB9XG4gICAgICAgIC5jb250cm9sLWJ0bi5hY3RpdmUgeyBiYWNrZ3JvdW5kOiB2YXIoLS1wcmltYXJ5LWRpbSk7IGJvcmRlci1jb2xvcjogdmFyKC0tcHJpbWFyeSk7IGNvbG9yOiB2YXIoLS1wcmltYXJ5KTsgfVxuICAgICAgICAuY29udHJvbC1idG4ud2FybmluZzpob3ZlciB7IGJvcmRlci1jb2xvcjogdmFyKC0tZGFuZ2VyKTsgY29sb3I6IHZhcigtLWRhbmdlcik7IGJhY2tncm91bmQ6IHJnYmEoMjU1LDQyLDQyLDAuMSk7IH1cblxuICAgICAgICAvKiAtLS0gTUFJTiBTVEFHRSAtLS0gKi9cbiAgICAgICAgLm1haW4tc3RhZ2Uge1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgZmxleDogMTtcbiAgICAgICAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG4gICAgICAgICAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgICAgICAgfVxuXG4gICAgICAgIC8qIC0tLSBDSEFUIElOVEVSRkFDRSAtLS0gKi9cbiAgICAgICAgLmNoYXQtaW50ZXJmYWNlIHtcbiAgICAgICAgICBmbGV4OiAxO1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgICAgICAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG4gICAgICAgICAgYmFja2dyb3VuZDogcmFkaWFsLWdyYWRpZW50KGNpcmNsZSBhdCA1MCUgMzAlLCAjMTExODI3IDAlLCAjMDUwNTA1IDYwJSk7XG4gICAgICAgIH1cblxuICAgICAgICAubWVzc2FnZXMtYXJlYSB7XG4gICAgICAgICAgZmxleDogMTtcbiAgICAgICAgICBvdmVyZmxvdy15OiBhdXRvO1xuICAgICAgICAgIHBhZGRpbmc6IDIwcHggMjBweCAxMDBweCAyMHB4OyAvKiBQYWRkaW5nIGJvdHRvbSBmb3Igc2Nyb2xsIGNsZWFyYW5jZSAqL1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgICAgICAgICBnYXA6IDI0cHg7XG4gICAgICAgICAgbWF4LXdpZHRoOiAxMDAwcHg7XG4gICAgICAgICAgd2lkdGg6IDEwMCU7XG4gICAgICAgICAgbWFyZ2luOiAwIGF1dG87XG4gICAgICAgIH1cblxuICAgICAgICAuZW1wdHktc3RhdGUge1xuICAgICAgICAgIHRleHQtYWxpZ246IGNlbnRlcjtcbiAgICAgICAgICBtYXJnaW4tdG9wOiAyMHZoO1xuICAgICAgICAgIGNvbG9yOiB2YXIoLS10ZXh0LW11dGVkKTtcbiAgICAgICAgfVxuICAgICAgICAuZW1wdHktaWNvbiB7IGZvbnQtc2l6ZTogNDBweDsgbWFyZ2luLWJvdHRvbTogMjBweDsgb3BhY2l0eTogMC4yOyB9XG5cbiAgICAgICAgLyogTWVzc2FnZSBCdWJibGVzICovXG4gICAgICAgIC5tZXNzYWdlLXJvdyB7IGRpc3BsYXk6IGZsZXg7IHdpZHRoOiAxMDAlOyBtYXJnaW4tdG9wOiAxMHB4OyB9XG4gICAgICAgIC5tZXNzYWdlLXJvdy51c2VyIHsganVzdGlmeS1jb250ZW50OiBmbGV4LWVuZDsgfVxuICAgICAgICBcbiAgICAgICAgLm1lc3NhZ2UtY29udGVudC13cmFwcGVyIHsgZGlzcGxheTogZmxleDsgZ2FwOiAxMnB4OyBtYXgtd2lkdGg6IDgwJTsgfVxuICAgICAgICAubWVzc2FnZS1yb3cudXNlciAubWVzc2FnZS1jb250ZW50LXdyYXBwZXIgeyBmbGV4LWRpcmVjdGlvbjogcm93LXJldmVyc2U7IH1cblxuICAgICAgICAuYXZhdGFyIHtcbiAgICAgICAgICB3aWR0aDogMzJweDsgaGVpZ2h0OiAzMnB4O1xuICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDRweDtcbiAgICAgICAgICBkaXNwbGF5OiBmbGV4OyBhbGlnbi1pdGVtczogY2VudGVyOyBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjtcbiAgICAgICAgICBmb250LXNpemU6IDEwcHg7IGZvbnQtd2VpZ2h0OiBib2xkO1xuICAgICAgICAgIGZsZXgtc2hyaW5rOiAwO1xuICAgICAgICB9XG4gICAgICAgIC5hdmF0YXIubW9kZWwgeyBiYWNrZ3JvdW5kOiB2YXIoLS1wcmltYXJ5LWRpbSk7IGNvbG9yOiB2YXIoLS1wcmltYXJ5KTsgYm9yZGVyOiAxcHggc29saWQgdmFyKC0tcHJpbWFyeSk7IH1cblxuICAgICAgICAubWVzc2FnZS1idWJibGUge1xuICAgICAgICAgIGJhY2tncm91bmQ6ICMxZTI5M2I7XG4gICAgICAgICAgcGFkZGluZzogMTZweCAyMHB4O1xuICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDEycHg7XG4gICAgICAgICAgYm9yZGVyOiAxcHggc29saWQgcmdiYSgyNTUsMjU1LDI1NSwwLjA1KTtcbiAgICAgICAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG4gICAgICAgICAgYm94LXNoYWRvdzogMCA0cHggNnB4IHJnYmEoMCwwLDAsMC4xKTtcbiAgICAgICAgfVxuICAgICAgICAubWVzc2FnZS1yb3cudXNlciAubWVzc2FnZS1idWJibGUge1xuICAgICAgICAgIGJhY2tncm91bmQ6ICMwZjE3MmE7XG4gICAgICAgICAgYm9yZGVyLWNvbG9yOiB2YXIoLS1ib3JkZXItZGltKTtcbiAgICAgICAgICBib3JkZXItYm90dG9tLXJpZ2h0LXJhZGl1czogMnB4O1xuICAgICAgICB9XG4gICAgICAgIC5tZXNzYWdlLXJvdy5tb2RlbCAubWVzc2FnZS1idWJibGUge1xuICAgICAgICAgIGJhY2tncm91bmQ6IHJnYmEoMCwgMjQzLCAyNTUsIDAuMDMpO1xuICAgICAgICAgIGJvcmRlci1jb2xvcjogcmdiYSgwLCAyNDMsIDI1NSwgMC4yKTtcbiAgICAgICAgICBib3JkZXItdG9wLWxlZnQtcmFkaXVzOiAycHg7XG4gICAgICAgIH1cblxuICAgICAgICAubWVzc2FnZS1oZWFkZXIgeyBkaXNwbGF5OiBmbGV4OyBqdXN0aWZ5LWNvbnRlbnQ6IHNwYWNlLWJldHdlZW47IGdhcDogMTJweDsgbWFyZ2luLWJvdHRvbTogOHB4OyBmb250LXNpemU6IDEwcHg7IG9wYWNpdHk6IDAuNjsgdGV4dC10cmFuc2Zvcm06IHVwcGVyY2FzZTsgbGV0dGVyLXNwYWNpbmc6IDAuNXB4OyB9XG4gICAgICAgIC50ZXh0LWNvbnRlbnQgeyBmb250LXNpemU6IDE1cHg7IGxpbmUtaGVpZ2h0OiAxLjY7IHdoaXRlLXNwYWNlOiBwcmUtd3JhcDsgfVxuXG4gICAgICAgIC5hdHRhY2htZW50LWdhbGxlcnkgeyBkaXNwbGF5OiBmbGV4OyBmbGV4LXdyYXA6IHdyYXA7IGdhcDogOHB4OyBtYXJnaW4tYm90dG9tOiAxMnB4OyB9XG4gICAgICAgIC5hdHQtaXRlbSBpbWcgeyBoZWlnaHQ6IDEyMHB4OyBib3JkZXItcmFkaXVzOiA0cHg7IGJvcmRlcjogMXB4IHNvbGlkICMzMzM7IH1cbiAgICAgICAgLmZpbGUtcGlsbCB7IHBhZGRpbmc6IDRweCA4cHg7IGJhY2tncm91bmQ6ICMwMDA7IGJvcmRlcjogMXB4IHNvbGlkICMzMzM7IGZvbnQtc2l6ZTogMTBweDsgY29sb3I6IHZhcigtLXByaW1hcnkpOyBib3JkZXItcmFkaXVzOiA0cHg7IH1cblxuICAgICAgICAubWljcm8tcXVhbGlhIHsgbWFyZ2luLXRvcDogOHB4OyBmb250LXNpemU6IDEwcHg7IGZvbnQtZmFtaWx5OiAnT3JiaXRyb24nOyBvcGFjaXR5OiAwLjg7IHRleHQtYWxpZ246IHJpZ2h0OyBib3JkZXItdG9wOiAxcHggc29saWQgcmdiYSgyNTUsMjU1LDI1NSwwLjA1KTsgcGFkZGluZy10b3A6IDRweDsgfVxuXG4gICAgICAgIC8qIFR5cGluZyBJbmRpY2F0b3IgKi9cbiAgICAgICAgLnR5cGluZy1pbmRpY2F0b3Igc3BhbiB7XG4gICAgICAgICAgZGlzcGxheTogaW5saW5lLWJsb2NrOyB3aWR0aDogNnB4OyBoZWlnaHQ6IDZweDsgYmFja2dyb3VuZDogdmFyKC0tdGV4dC1tdXRlZCk7IGJvcmRlci1yYWRpdXM6IDUwJTtcbiAgICAgICAgICBhbmltYXRpb246IGJvdW5jZSAxLjRzIGluZmluaXRlIGVhc2UtaW4tb3V0IGJvdGg7IG1hcmdpbjogMCAycHg7XG4gICAgICAgIH1cbiAgICAgICAgLnR5cGluZy1pbmRpY2F0b3Igc3BhbjpudGgtY2hpbGQoMSkgeyBhbmltYXRpb24tZGVsYXk6IC0wLjMyczsgfVxuICAgICAgICAudHlwaW5nLWluZGljYXRvciBzcGFuOm50aC1jaGlsZCgyKSB7IGFuaW1hdGlvbi1kZWxheTogLTAuMTZzOyB9XG4gICAgICAgIEBrZXlmcmFtZXMgYm91bmNlIHsgMCUsIDgwJSwgMTAwJSB7IHRyYW5zZm9ybTogc2NhbGUoMCk7IH0gNDAlIHsgdHJhbnNmb3JtOiBzY2FsZSgxKTsgfSB9XG5cbiAgICAgICAgLyogLS0tIElOUFVUIERPQ0sgLS0tICovXG4gICAgICAgIC5pbnB1dC1kb2NrIHtcbiAgICAgICAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gICAgICAgICAgYm90dG9tOiAwOyBsZWZ0OiAwOyByaWdodDogMDtcbiAgICAgICAgICBwYWRkaW5nOiAyNHB4O1xuICAgICAgICAgIGJhY2tncm91bmQ6IGxpbmVhci1ncmFkaWVudCh0byB0b3AsICMwNTA1MDUgODAlLCB0cmFuc3BhcmVudCk7XG4gICAgICAgICAgZGlzcGxheTogZmxleDtcbiAgICAgICAgICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjtcbiAgICAgICAgfVxuXG4gICAgICAgIC5pbnB1dC1jb250YWluZXIge1xuICAgICAgICAgIHdpZHRoOiAxMDAlO1xuICAgICAgICAgIG1heC13aWR0aDogOTAwcHg7XG4gICAgICAgICAgYmFja2dyb3VuZDogcmdiYSgxNSwgMjMsIDQyLCAwLjgpO1xuICAgICAgICAgIGJhY2tkcm9wLWZpbHRlcjogYmx1cigxMnB4KTtcbiAgICAgICAgICBib3JkZXI6IDFweCBzb2xpZCB2YXIoLS1ib3JkZXItZGltKTtcbiAgICAgICAgICBib3JkZXItcmFkaXVzOiAxMnB4O1xuICAgICAgICAgIHBhZGRpbmc6IDEycHg7XG4gICAgICAgICAgYm94LXNoYWRvdzogMCAwIDIwcHggcmdiYSgwLDAsMCwwLjUpO1xuICAgICAgICAgIHRyYW5zaXRpb246IGJvcmRlci1jb2xvciAwLjJzO1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgICAgICAgICBnYXA6IDhweDtcbiAgICAgICAgfVxuICAgICAgICAuaW5wdXQtY29udGFpbmVyOmZvY3VzLXdpdGhpbiB7XG4gICAgICAgICAgYm9yZGVyLWNvbG9yOiB2YXIoLS1wcmltYXJ5KTtcbiAgICAgICAgICBib3gtc2hhZG93OiAwIDAgMjBweCByZ2JhKDAsIDI0MywgMjU1LCAwLjEpO1xuICAgICAgICB9XG5cbiAgICAgICAgLmF0dGFjaG1lbnRzLXByZXZpZXctYmFyIHsgZGlzcGxheTogZmxleDsgZ2FwOiA4cHg7IGZsZXgtd3JhcDogd3JhcDsgcGFkZGluZy1ib3R0b206IDhweDsgYm9yZGVyLWJvdHRvbTogMXB4IHNvbGlkIHJnYmEoMjU1LDI1NSwyNTUsMC4wNSk7IH1cbiAgICAgICAgLnByZXZpZXctY2hpcCB7IGJhY2tncm91bmQ6ICMwMDA7IHBhZGRpbmc6IDRweCA4cHg7IGJvcmRlci1yYWRpdXM6IDRweDsgYm9yZGVyOiAxcHggc29saWQgIzMzMzsgZGlzcGxheTogZmxleDsgYWxpZ24taXRlbXM6IGNlbnRlcjsgZ2FwOiA2cHg7IGZvbnQtc2l6ZTogMTFweDsgY29sb3I6ICNmZmY7IH1cbiAgICAgICAgLnByZXZpZXctY2hpcCBidXR0b24geyBiYWNrZ3JvdW5kOiBub25lOyBib3JkZXI6IG5vbmU7IGNvbG9yOiAjNjY2OyBjdXJzb3I6IHBvaW50ZXI7IGZvbnQtc2l6ZTogMTRweDsgfVxuICAgICAgICAucHJldmlldy1jaGlwIGJ1dHRvbjpob3ZlciB7IGNvbG9yOiAjZmZmOyB9XG5cbiAgICAgICAgLmlucHV0LWJhciB7IGRpc3BsYXk6IGZsZXg7IGFsaWduLWl0ZW1zOiBmbGV4LWVuZDsgZ2FwOiAxMnB4OyB9XG4gICAgICAgIFxuICAgICAgICAuYXR0YWNoLWJ0biB7XG4gICAgICAgICAgYmFja2dyb3VuZDogdHJhbnNwYXJlbnQ7IGJvcmRlcjogbm9uZTsgY29sb3I6IHZhcigtLXRleHQtbXV0ZWQpOyBjdXJzb3I6IHBvaW50ZXI7IHBhZGRpbmc6IDhweDsgYm9yZGVyLXJhZGl1czogNnB4O1xuICAgICAgICAgIHRyYW5zaXRpb246IDAuMnM7XG4gICAgICAgIH1cbiAgICAgICAgLmF0dGFjaC1idG46aG92ZXIgeyBiYWNrZ3JvdW5kOiByZ2JhKDI1NSwyNTUsMjU1LDAuMDUpOyBjb2xvcjogdmFyKC0tcHJpbWFyeSk7IH1cblxuICAgICAgICB0ZXh0YXJlYSB7XG4gICAgICAgICAgZmxleDogMTsgYmFja2dyb3VuZDogdHJhbnNwYXJlbnQ7IGJvcmRlcjogbm9uZTsgY29sb3I6ICNmZmY7XG4gICAgICAgICAgZm9udC1mYW1pbHk6IGluaGVyaXQ7IGZvbnQtc2l6ZTogMTZweDsgbGluZS1oZWlnaHQ6IDEuNTtcbiAgICAgICAgICByZXNpemU6IG5vbmU7IG91dGxpbmU6IG5vbmU7IG1pbi1oZWlnaHQ6IDI0cHg7IG1heC1oZWlnaHQ6IDE1MHB4O1xuICAgICAgICAgIHBhZGRpbmc6IDhweCAwO1xuICAgICAgICB9XG5cbiAgICAgICAgLnNlbmQtYnRuIHtcbiAgICAgICAgICBiYWNrZ3JvdW5kOiB2YXIoLS1wcmltYXJ5KTsgY29sb3I6ICMwMDA7IGJvcmRlcjogbm9uZTtcbiAgICAgICAgICBmb250LWZhbWlseTogJ09yYml0cm9uJzsgZm9udC13ZWlnaHQ6IGJvbGQ7IGZvbnQtc2l6ZTogMTJweDtcbiAgICAgICAgICBwYWRkaW5nOiA4cHggMTZweDsgYm9yZGVyLXJhZGl1czogNnB4OyBjdXJzb3I6IHBvaW50ZXI7XG4gICAgICAgICAgdHJhbnNpdGlvbjogMC4yczsgaGVpZ2h0OiAzNnB4O1xuICAgICAgICB9XG4gICAgICAgIC5zZW5kLWJ0bjpob3Zlcjpub3QoOmRpc2FibGVkKSB7IGJveC1zaGFkb3c6IDAgMCAxNXB4IHZhcigtLXByaW1hcnkpOyB0cmFuc2Zvcm06IHRyYW5zbGF0ZVkoLTFweCk7IH1cbiAgICAgICAgLnNlbmQtYnRuOmRpc2FibGVkIHsgb3BhY2l0eTogMC40OyBjdXJzb3I6IG5vdC1hbGxvd2VkOyBiYWNrZ3JvdW5kOiAjMzMzOyBjb2xvcjogIzY2NjsgfVxuXG4gICAgICAgIC8qIC0tLSBDT1JURVggU0lERUJBUiAtLS0gKi9cbiAgICAgICAgLmNvcnRleC1zaWRlYmFyIHtcbiAgICAgICAgICB3aWR0aDogMDtcbiAgICAgICAgICBiYWNrZ3JvdW5kOiAjMDgwYTBjO1xuICAgICAgICAgIGJvcmRlci1sZWZ0OiAxcHggc29saWQgdmFyKC0tYm9yZGVyLWRpbSk7XG4gICAgICAgICAgZGlzcGxheTogZmxleDtcbiAgICAgICAgICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xuICAgICAgICAgIHRyYW5zaXRpb246IHdpZHRoIDAuM3MgY3ViaWMtYmV6aWVyKDAuMTYsIDEsIDAuMywgMSk7XG4gICAgICAgICAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgICAgICAgfVxuICAgICAgICAuY29ydGV4LXNpZGViYXIudmlzaWJsZSB7IHdpZHRoOiAzNTBweDsgfVxuXG4gICAgICAgIC5zaWRlYmFyLWhlYWRlciB7XG4gICAgICAgICAgcGFkZGluZzogMTZweDtcbiAgICAgICAgICBib3JkZXItYm90dG9tOiAxcHggc29saWQgdmFyKC0tYm9yZGVyLWRpbSk7XG4gICAgICAgICAgZm9udC1mYW1pbHk6ICdPcmJpdHJvbic7IGZvbnQtc2l6ZTogMTBweDsgY29sb3I6IHZhcigtLXRleHQtbXV0ZWQpO1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7IGp1c3RpZnktY29udGVudDogc3BhY2UtYmV0d2VlbjsgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAgICAgICAgICB3aGl0ZS1zcGFjZTogbm93cmFwO1xuICAgICAgICB9XG4gICAgICAgIC5saXZlLWRvdCB7IHdpZHRoOiA2cHg7IGhlaWdodDogNnB4OyBiYWNrZ3JvdW5kOiB2YXIoLS1wcmltYXJ5KTsgYm9yZGVyLXJhZGl1czogNTAlOyBib3gtc2hhZG93OiAwIDAgOHB4IHZhcigtLXByaW1hcnkpOyB9XG5cbiAgICAgICAgLnRob3VnaHRzLWZlZWQge1xuICAgICAgICAgIGZsZXg6IDE7IG92ZXJmbG93LXk6IGF1dG87IHBhZGRpbmc6IDE2cHg7XG4gICAgICAgICAgZGlzcGxheTogZmxleDsgZmxleC1kaXJlY3Rpb246IGNvbHVtbjsgZ2FwOiAxMnB4O1xuICAgICAgICB9XG4gICAgICAgIC50aG91Z2h0LXBsYWNlaG9sZGVyIHsgY29sb3I6ICMzMzM7IGZvbnQtc3R5bGU6IGl0YWxpYzsgZm9udC1zaXplOiAxMnB4OyB0ZXh0LWFsaWduOiBjZW50ZXI7IG1hcmdpbi10b3A6IDQwcHg7IH1cblxuICAgICAgICAudGhvdWdodC1jYXJkIHtcbiAgICAgICAgICBiYWNrZ3JvdW5kOiAjMGUxMjE2O1xuICAgICAgICAgIGJvcmRlcjogMXB4IHNvbGlkICMxYTIzMmU7XG4gICAgICAgICAgYm9yZGVyLWxlZnQ6IDJweCBzb2xpZCB2YXIoLS10ZXh0LW11dGVkKTtcbiAgICAgICAgICBwYWRkaW5nOiAxMnB4O1xuICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDRweDtcbiAgICAgICAgICBmb250LWZhbWlseTogJ0pldEJyYWlucyBNb25vJywgbW9ub3NwYWNlO1xuICAgICAgICB9XG4gICAgICAgIC50aG91Z2h0LWhlYWRlciB7IGRpc3BsYXk6IGZsZXg7IGp1c3RpZnktY29udGVudDogc3BhY2UtYmV0d2VlbjsgZm9udC1zaXplOiA5cHg7IGNvbG9yOiAjNTU1OyBtYXJnaW4tYm90dG9tOiA2cHg7IH1cbiAgICAgICAgLnRob3VnaHQtYm9keSB7IGZvbnQtc2l6ZTogMTFweDsgY29sb3I6IHZhcigtLXRleHQtc2Vjb25kYXJ5KTsgbGluZS1oZWlnaHQ6IDEuNDsgfVxuICAgICAgICBcbiAgICAgICAgLnRob3VnaHQtbWV0cmljcyB7IGRpc3BsYXk6IGZsZXg7IGdhcDogOHB4OyBtYXJnaW4tdG9wOiA4cHg7IH1cbiAgICAgICAgLm1ldHJpYyB7IGRpc3BsYXk6IGZsZXg7IGFsaWduLWl0ZW1zOiBjZW50ZXI7IGdhcDogNHB4OyBmbGV4OiAxOyB9XG4gICAgICAgIC5tZXRyaWMgLmxibCB7IGZvbnQtc2l6ZTogOHB4OyBjb2xvcjogIzQ0NDsgfVxuICAgICAgICAubWV0cmljIC5iYXIgeyBmbGV4OiAxOyBoZWlnaHQ6IDJweDsgYmFja2dyb3VuZDogIzIyMjsgfVxuICAgICAgICAubWV0cmljIC5iYXIgZGl2IHsgaGVpZ2h0OiAxMDAlOyBiYWNrZ3JvdW5kOiB2YXIoLS1wcmltYXJ5LWRpbSk7IH1cblxuICAgICAgICAudmV0by1nYXRlLW92ZXJsYXkge1xuICAgICAgICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICAgICAgICB0b3A6IDUwJTsgbGVmdDogNTAlO1xuICAgICAgICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlKC01MCUsIC01MCUpO1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgICAgICAgICBhbGlnbi1pdGVtczogY2VudGVyO1xuICAgICAgICAgIGdhcDogMTJweDtcbiAgICAgICAgICB6LWluZGV4OiAxMDA7XG4gICAgICAgIH1cbiAgICAgICAgLnZldG8tYnRuIHtcbiAgICAgICAgICBiYWNrZ3JvdW5kOiB2YXIoLS1kYW5nZXIpO1xuICAgICAgICAgIGNvbG9yOiAjZmZmO1xuICAgICAgICAgIGJvcmRlcjogbm9uZTtcbiAgICAgICAgICBwYWRkaW5nOiAxMnB4IDI0cHg7XG4gICAgICAgICAgYm9yZGVyLXJhZGl1czogOTlweDtcbiAgICAgICAgICBmb250LWZhbWlseTogJ09yYml0cm9uJztcbiAgICAgICAgICBmb250LXdlaWdodDogYm9sZDtcbiAgICAgICAgICBmb250LXNpemU6IDE0cHg7XG4gICAgICAgICAgY3Vyc29yOiBwb2ludGVyO1xuICAgICAgICAgIGRpc3BsYXk6IGZsZXg7XG4gICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAgICAgICAgICBnYXA6IDEwcHg7XG4gICAgICAgICAgYm94LXNoYWRvdzogMCAwIDMwcHggcmdiYSgyNTUsIDQyLCA0MiwgMC40KTtcbiAgICAgICAgfVxuICAgICAgICAudmV0by10aW1lciB7XG4gICAgICAgICAgZm9udC1zaXplOiAxMHB4O1xuICAgICAgICAgIGNvbG9yOiB2YXIoLS1kYW5nZXIpO1xuICAgICAgICAgIGZvbnQtZmFtaWx5OiAnT3JiaXRyb24nO1xuICAgICAgICAgIGxldHRlci1zcGFjaW5nOiAycHg7XG4gICAgICAgICAgYW5pbWF0aW9uOiBwdWxzZSAwLjVzIGluZmluaXRlO1xuICAgICAgICB9XG4gICAgICAgIEBrZXlmcmFtZXMgcHVsc2UgeyAwJSB7IG9wYWNpdHk6IDAuNDsgfSA1MCUgeyBvcGFjaXR5OiAxOyB9IDEwMCUgeyBvcGFjaXR5OiAwLjQ7IH0gfVxuICAgICAgYH08L3N0eWxlPlxuICAgIDwvZGl2PlxuICApO1xufVxuXG5jb25zdCByb290ID0gY3JlYXRlUm9vdChkb2N1bWVudC5nZXRFbGVtZW50QnlJZChcInJvb3RcIikhKTtcbnJvb3QucmVuZGVyKDxBcHAgLz4pOyJdLCJmaWxlIjoiL2FwcC9hcHBsZXQvaW5kZXgudHN4In0=