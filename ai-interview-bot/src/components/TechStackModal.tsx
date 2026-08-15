import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Cpu, Server, Layout, Sparkles, Mic, Code2, Zap, ShieldCheck } from 'lucide-react';

interface TechStackModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeProvider: string;
}

export const TechStackModal: React.FC<TechStackModalProps> = ({
  isOpen,
  onClose,
  activeProvider,
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div 
        id="tech-stack-backdrop"
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          id="tech-stack-dialog"
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-900 border border-slate-700/80 rounded-2xl p-6 shadow-2xl text-slate-100"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 mb-5 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Application Architecture & Tech Stack</h3>
                <p className="text-xs text-slate-400">Full-stack LLM AI Interview Bot breakdown</p>
              </div>
            </div>
            <button
              id="close-tech-stack-btn"
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Active LLM Banner */}
          <div className="p-4 mb-6 rounded-xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-indigo-950/60 border border-indigo-500/30 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-400 animate-ping" />
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-indigo-300">Active Inference Engine</span>
                <p className="text-sm font-semibold text-white">{activeProvider || 'Groq Llama 3.3 70B Versatile'}</p>
              </div>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-mono">
              Live & Ready
            </span>
          </div>

          {/* Detailed Stack Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* LLM Layer */}
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center gap-2 mb-2 text-indigo-400">
                <Cpu className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">1. LLM & AI Engine</span>
              </div>
              <ul className="text-xs space-y-1.5 text-slate-300">
                <li className="flex items-start gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" />
                  <span><strong>Groq Cloud API:</strong> Llama 3.3 70B Versatile for sub-second ultra-low latency question generation & deep evaluation.</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400 mt-0.5 shrink-0" />
                  <span><strong>Google GenAI SDK:</strong> Multi-tiered fallback with Gemini 2.5 Flash for continuous reliability.</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                  <span><strong>Structured JSON Output:</strong> Zero-hallucination calibrated scoring across 4 standardized interview rubrics.</span>
                </li>
              </ul>
            </div>

            {/* Backend Server */}
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center gap-2 mb-2 text-blue-400">
                <Server className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">2. Backend Server & APIs</span>
              </div>
              <ul className="text-xs space-y-1.5 text-slate-300">
                <li>• <strong>Express.js / Node.js:</strong> Full-stack server proxying all secret API keys securely on the server side.</li>
                <li>• <strong>Endpoints:</strong>
                  <div className="mt-1 font-mono text-[11px] text-slate-400 bg-slate-900/80 p-2 rounded border border-slate-800">
                    <div>POST /api/interview/start</div>
                    <div>POST /api/interview/evaluate-and-next</div>
                    <div>POST /api/interview/generate-report</div>
                  </div>
                </li>
              </ul>
            </div>

            {/* Frontend Framework */}
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center gap-2 mb-2 text-emerald-400">
                <Layout className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">3. Frontend & Styling</span>
              </div>
              <ul className="text-xs space-y-1.5 text-slate-300">
                <li>• <strong>React 19 & TypeScript:</strong> Strict type safety for turns, scores, personas, and study roadmaps.</li>
                <li>• <strong>Tailwind CSS v4:</strong> Dark slate palette with high-contrast optical hierarchy and responsive layouts.</li>
                <li>• <strong>Motion (Framer Motion):</strong> Smooth transitions between question rounds, score dials, and evaluation cards.</li>
                <li>• <strong>Lucide React:</strong> Consistent visual icon taxonomy.</li>
              </ul>
            </div>

            {/* Voice & Realtime Features */}
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center gap-2 mb-2 text-purple-400">
                <Mic className="w-4 h-4" />
                <span className="text-xs font-semibold uppercase tracking-wider">4. Voice & Interactive Features</span>
              </div>
              <ul className="text-xs space-y-1.5 text-slate-300">
                <li>• <strong>Web Speech Recognition:</strong> Real-time microphone speech-to-text dictation so users can answer out loud.</li>
                <li>• <strong>Groq Whisper Fallback:</strong> Automatic server-side transcription (whisper-large-v3) when the browser's cloud speech service is unreachable or blocked.</li>
                <li>• <strong>Speech Synthesis (TTS):</strong> Audio interviewer playback with natural English cadence and customizable persona voices.</li>
                <li>• <strong>Canvas Confetti:</strong> Animated reward celebration for hiring achievements.</li>
                <li>• <strong>Local History:</strong> Persistent session storage for review and export.</li>
              </ul>
            </div>
          </div>

          <div className="flex justify-end pt-2 border-t border-slate-800">
            <button
              id="close-stack-modal-footer-btn"
              onClick={onClose}
              className="px-5 py-2 text-sm font-medium rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
            >
              Got it
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
