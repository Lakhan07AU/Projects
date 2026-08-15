/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Bot, 
  Sparkles, 
  Code2, 
  History, 
  Zap, 
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { 
  InterviewConfig, 
  InterviewTurn, 
  FinalReport, 
  SavedInterviewSession 
} from './types';
import { RoleSelector } from './components/RoleSelector';
import { ActiveInterview } from './components/ActiveInterview';
import { FinalScorecard } from './components/FinalScorecard';
import { TechStackModal } from './components/TechStackModal';
import { PastInterviewsModal } from './components/PastInterviewsModal';

type AppState = 'setup' | 'interviewing' | 'report';

const STORAGE_KEY = 'ai_interview_bot_sessions_v1';

export default function App() {
  const [appState, setAppState] = useState<AppState>('setup');
  const [config, setConfig] = useState<InterviewConfig | null>(null);
  const [turns, setTurns] = useState<InterviewTurn[]>([]);
  const [currentTurnIndex, setCurrentTurnIndex] = useState(0);
  const [finalReport, setFinalReport] = useState<FinalReport | null>(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modals
  const [isTechStackOpen, setIsTechStackOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [activeProvider, setActiveProvider] = useState<string>('Groq (Llama 3.3 70B)');

  // Persistent session history
  const [savedSessions, setSavedSessions] = useState<SavedInterviewSession[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });

  // Check health on mount
  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        if (data.activeProvider) {
          setActiveProvider(data.activeProvider);
        }
      })
      .catch(err => console.warn('Health check note:', err));
  }, []);

  // Save session when final report is generated
  const persistSession = (cfg: InterviewConfig, completedTurns: InterviewTurn[], report: FinalReport) => {
    const newSession: SavedInterviewSession = {
      id: 'session_' + Date.now(),
      timestamp: Date.now(),
      config: cfg,
      turns: completedTurns,
      report,
      durationSeconds: completedTurns.reduce((acc, t) => acc + (t.timeSpentSeconds || 60), 0)
    };

    const updated = [newSession, ...savedSessions].slice(0, 25);
    setSavedSessions(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (e) {
      console.warn('Failed to save to localStorage', e);
    }
  };

  const handleClearHistory = () => {
    setSavedSessions([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Step 1: Start Interview and request Question 1
  const handleStartInterview = async (newConfig: InterviewConfig) => {
    setIsLoading(true);
    setErrorMessage(null);
    setConfig(newConfig);

    try {
      const response = await fetch('/api/interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: newConfig }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to start interview');
      }

      const data = await response.json();
      const firstTurn: InterviewTurn = {
        questionNumber: 1,
        question: data.firstTurn.question,
        category: data.firstTurn.category || 'Architecture & Foundations',
        difficulty: data.firstTurn.difficulty || 'Standard',
        contextTip: data.firstTurn.contextTip,
      };

      setTurns([firstTurn]);
      setCurrentTurnIndex(0);
      setAppState('interviewing');
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || 'Error generating question. Please verify your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Evaluate User Answer & Receive next question or prepare report
  const handleEvaluateAnswer = async (userAnswer: string) => {
    if (!config || !turns[currentTurnIndex]) return;

    setIsEvaluating(true);
    setErrorMessage(null);

    const currentTurn = turns[currentTurnIndex];
    const isLast = currentTurnIndex + 1 >= config.totalQuestions;

    try {
      const response = await fetch('/api/interview/evaluate-and-next', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config,
          currentQuestion: currentTurn,
          userAnswer,
          previousTurns: turns.slice(0, currentTurnIndex),
          questionNumber: currentTurnIndex + 1,
          isLastQuestion: isLast,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to evaluate answer');
      }

      const data = await response.json();
      const evaluatedTurn: InterviewTurn = {
        ...currentTurn,
        userAnswer,
        evaluation: data.evaluation,
      };

      const updatedTurns = [...turns];
      updatedTurns[currentTurnIndex] = evaluatedTurn;

      // If next question returned, append it
      if (data.nextQuestion && !isLast) {
        const nextTurn: InterviewTurn = {
          questionNumber: currentTurnIndex + 2,
          question: data.nextQuestion.question,
          category: data.nextQuestion.category || 'Deep Dive',
          difficulty: data.nextQuestion.difficulty || 'Challenging',
          contextTip: data.nextQuestion.contextTip,
        };
        updatedTurns.push(nextTurn);
      }

      setTurns(updatedTurns);
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || 'Failed to evaluate answer. Please try again.');
    } finally {
      setIsEvaluating(false);
    }
  };

  // Step 3: Advance to next question turn
  const handleProceedToNextQuestion = () => {
    if (currentTurnIndex + 1 < turns.length) {
      setCurrentTurnIndex(prev => prev + 1);
    }
  };

  // Capture how long the candidate spent on the current answer
  const handleRecordTime = (seconds: number) => {
    setTurns(prev => {
      const updated = [...prev];
      const idx = currentTurnIndex;
      if (updated[idx] && updated[idx].evaluation && seconds > 0) {
        updated[idx] = { ...updated[idx], timeSpentSeconds: seconds };
      }
      return updated;
    });
  };

  // Step 4: Finish interview & Generate Final Scorecard & 4-Week Study Roadmap
  const handleFinishInterview = async () => {
    if (!config || turns.length === 0) return;

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch('/api/interview/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config,
          turns,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to generate final report');
      }

      const data = await response.json();
      setFinalReport(data.report);
      persistSession(config, turns, data.report);
      setAppState('report');
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || 'Failed to generate comprehensive scorecard.');
    } finally {
      setIsLoading(false);
    }
  };

  // Load past session from history
  const handleSelectPastSession = (session: SavedInterviewSession) => {
    setConfig(session.config);
    setTurns(session.turns);
    if (session.report) {
      setFinalReport(session.report);
      setAppState('report');
    } else {
      setCurrentTurnIndex(0);
      setAppState('interviewing');
    }
    setIsHistoryOpen(false);
  };

  // Restart / Reset
  const handleRestart = () => {
    setAppState('setup');
    setTurns([]);
    setCurrentTurnIndex(0);
    setFinalReport(null);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white flex flex-col justify-between">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Logo & Title */}
          <div 
            id="app-brand-btn"
            onClick={handleRestart}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base text-white tracking-tight">AI Interview Bot</span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                  v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono hidden sm:block">
                Interactive Mock Engineering & Leadership Practice
              </p>
            </div>
          </div>

          {/* Right Action Controls */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Live LLM Engine Indicator */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
              <Zap className="w-3.5 h-3.5 text-amber-400 fill-amber-400 animate-pulse" />
              <span>{activeProvider}</span>
            </div>

            {/* Tech Stack Modal Button */}
            <button
              id="open-tech-stack-btn"
              onClick={() => setIsTechStackOpen(true)}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1.5"
            >
              <Code2 className="w-4 h-4 text-indigo-400" />
              <span className="hidden sm:inline">Tech Stack</span>
            </button>

            {/* Past History Modal Button */}
            <button
              id="open-history-btn"
              onClick={() => setIsHistoryOpen(true)}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 relative"
            >
              <History className="w-4 h-4 text-slate-400" />
              <span className="hidden sm:inline">History</span>
              {savedSessions.length > 0 && (
                <span className="w-2 h-2 rounded-full bg-indigo-500 absolute -top-0.5 -right-0.5" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Global Error Notice */}
      <AnimatePresence>
        {errorMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="max-w-4xl mx-auto px-4 mt-4 w-full"
          >
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="text-rose-400 hover:text-rose-200 font-semibold ml-2"
              >
                Dismiss
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Viewport Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full">
        {isLoading && appState === 'setup' ? (
          <div className="text-center py-24 space-y-4">
            <div className="w-12 h-12 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <div className="space-y-1">
              <h3 className="text-base font-semibold text-white">Initializing AI Interview Session...</h3>
              <p className="text-xs text-slate-400">Calibrating interview question with Groq Llama 3.3 70B & target persona</p>
            </div>
          </div>
        ) : appState === 'setup' ? (
          <RoleSelector
            onStartInterview={handleStartInterview}
            isLoading={isLoading}
          />
        ) : appState === 'interviewing' && config && turns[currentTurnIndex] ? (
          <ActiveInterview
            config={config}
            currentTurn={turns[currentTurnIndex]}
            turnIndex={currentTurnIndex}
            totalTurns={config.totalQuestions}
            isEvaluating={isEvaluating}
            isFinishingInterview={isLoading}
            onEvaluateAnswer={handleEvaluateAnswer}
            onRecordTime={handleRecordTime}
            onProceedToNextQuestion={handleProceedToNextQuestion}
            onFinishInterview={handleFinishInterview}
            onCancelInterview={handleRestart}
          />
        ) : appState === 'report' && config && finalReport ? (
          <FinalScorecard
            report={finalReport}
            config={config}
            turns={turns}
            onRestart={handleRestart}
          />
        ) : (
          <div className="text-center py-16">
            <button
              onClick={handleRestart}
              className="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold"
            >
              Reset Session
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 bg-slate-950 text-slate-500 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span>AI Interview Bot</span>
            <span>•</span>
            <span>Powered by Groq Cloud & Google Gemini</span>
          </div>
          <div className="flex items-center gap-4 text-[11px] font-mono">
            <span>Voice Input: Web Speech + Groq Whisper fallback</span>
            <span>•</span>
            <button
              onClick={() => setIsTechStackOpen(true)}
              className="text-indigo-400 hover:underline"
            >
              View Full Tech Stack
            </button>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <TechStackModal
        isOpen={isTechStackOpen}
        onClose={() => setIsTechStackOpen(false)}
        activeProvider={activeProvider}
      />

      <PastInterviewsModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        sessions={savedSessions}
        onSelectSession={handleSelectPastSession}
        onClearHistory={handleClearHistory}
      />
    </div>
  );
}
