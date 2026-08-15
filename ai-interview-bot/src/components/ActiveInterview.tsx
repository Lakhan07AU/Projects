import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Volume2, 
  VolumeX, 
  Mic, 
  MicOff, 
  Send, 
  CheckCircle2, 
  AlertTriangle, 
  Lightbulb, 
  BookOpen, 
  ChevronRight, 
  Clock, 
  Pause, 
  Play, 
  MessageSquare,
  Award,
  ListOrdered,
  AudioLines,
  Square,
  Command,
  CornerDownLeft,
  AlertCircle
} from 'lucide-react';
import { InterviewConfig, InterviewTurn, AnswerEvaluation } from '../types';
import { PERSONA_PROFILES, ROLE_PRESETS } from '../data/roles';
import {
  speakText,
  stopSpeaking,
  createSpeechRecognizer,
  getSpeechRecognitionSupport,
  getFriendlyMicError,
  isAudioRecordingSupported,
  createAudioRecorder,
  transcribeAudio,
} from '../utils/speech';

interface ActiveInterviewProps {
  config: InterviewConfig;
  currentTurn: InterviewTurn;
  turnIndex: number;
  totalTurns: number;
  isEvaluating: boolean;
  isFinishingInterview?: boolean;
  onEvaluateAnswer: (userAnswer: string) => void;
  onRecordTime?: (seconds: number) => void;
  onProceedToNextQuestion: () => void;
  onFinishInterview: () => void;
  onCancelInterview: () => void;
}

export const ActiveInterview: React.FC<ActiveInterviewProps> = ({
  config,
  currentTurn,
  turnIndex,
  totalTurns,
  isEvaluating,
  isFinishingInterview = false,
  onEvaluateAnswer,
  onRecordTime,
  onProceedToNextQuestion,
  onFinishInterview,
  onCancelInterview,
}) => {
  const [userAnswer, setUserAnswer] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [recordingMode, setRecordingMode] = useState<'wsapi' | 'recorder' | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [micSupported, setMicSupported] = useState(true);
  const [showTip, setShowTip] = useState(false);
  const [showExemplary, setShowExemplary] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(true);

  const recognitionRef = useRef<any>(null);
  const recorderRef = useRef<any>(null);
  const recordingTimerRef = useRef<any>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const shouldKeepListeningRef = useRef(false);
  const isEvaluatingRef = useRef(false);
  const recordingModeRef = useRef<'wsapi' | 'recorder' | null>(null);

  // Keep refs in sync for callbacks that close over stale state
  useEffect(() => {
    isEvaluatingRef.current = isEvaluating;
  }, [isEvaluating]);
  useEffect(() => {
    recordingModeRef.current = recordingMode;
  }, [recordingMode]);

  const activePersona = PERSONA_PROFILES.find(p => p.id === config.interviewerPersona) || PERSONA_PROFILES[0];
  const roleTitle = config.customRoleTitle || ROLE_PRESETS.find(r => r.id === config.roleId)?.title || config.roleId;

  // Auto-timer for answer duration
  useEffect(() => {
    let interval: any;
    if (isTimerRunning && !currentTurn.evaluation) {
      interval = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, currentTurn.evaluation]);

  // Detect microphone / speech recognition support once
  useEffect(() => {
    const support = getSpeechRecognitionSupport();
    const canRecord = isAudioRecordingSupported();
    setMicSupported(support.supported || canRecord);
    if (!support.supported && !canRecord) {
      setSpeechError(
        'Voice input is not supported in this browser. Please use Chrome or Edge, or type your answer.'
      );
    }
  }, []);

  // Persist the answer duration once evaluation feedback arrives
  useEffect(() => {
    if (currentTurn.evaluation && elapsedSeconds > 0) {
      onRecordTime?.(elapsedSeconds);
    }
  }, [currentTurn.evaluation]);

  const stopActiveRecorder = () => {
    recorderRef.current = null;
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    setRecordingSeconds(0);
  };

  // Reset state when new question turns arrive
  useEffect(() => {
    shouldKeepListeningRef.current = false;
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
    }
    if (recorderRef.current) {
      try {
        recorderRef.current.stop().catch(() => {});
      } catch {
        // ignore
      }
    }
    stopActiveRecorder();
    setUserAnswer(currentTurn.userAnswer || '');
    setInterimTranscript('');
    setShowTip(false);
    setShowExemplary(false);
    setElapsedSeconds(0);
    setIsTimerRunning(true);
    setIsListening(false);
    setIsTranscribing(false);
    setRecordingMode(null);
    stopSpeaking();
    setIsSpeaking(false);
  }, [currentTurn.questionNumber]);

  // Cleanup speech on unmount
  useEffect(() => {
    return () => {
      shouldKeepListeningRef.current = false;
      stopSpeaking();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
      if (recorderRef.current) {
        try {
          recorderRef.current.stop().catch(() => {});
        } catch {
          // ignore
        }
      }
      stopActiveRecorder();
    };
  }, []);

  // Handle TTS Question Readout
  const toggleTTS = () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
    } else {
      // Don't speak while capturing audio to avoid feedback
      if (isListening || isTranscribing) {
        return;
      }
      setIsSpeaking(true);
      speakText(currentTurn.question, undefined, () => setIsSpeaking(false));
    }
  };

  // Start a fresh recognizer session. Recreated on each start so the
  // recognizer can be reliably restarted after it ends unexpectedly.
  const startListening = () => {
    setSpeechError(null);
    setInterimTranscript('');

    // Stop any TTS playback so the mic does not pick it up
    stopSpeaking();
    setIsSpeaking(false);

    const recognizer = createSpeechRecognizer({
      onTranscript: (transcript, isFinal) => {
        if (isFinal) {
          setUserAnswer(prev => prev ? `${prev} ${transcript}` : transcript);
          setInterimTranscript('');
        } else {
          setInterimTranscript(transcript);
        }
      },
      onError: (err) => {
        const friendly = getFriendlyMicError(err);
        if (!friendly) return; // 'aborted' — user stopped, ignore
        if (err === 'no-speech' || err === 'audio-capture') {
          // Transient — keep listening via onEnd restart
          return;
        }
        shouldKeepListeningRef.current = false;
        if (err === 'network' || err === 'service-not-allowed') {
          // Chrome's cloud speech service is unreachable/disabled.
          // Fall back to local recording + server-side transcription.
          if (recognitionRef.current) {
            try {
              recognitionRef.current.stop();
            } catch {
              // ignore
            }
          }
          setIsListening(false);
          setInterimTranscript('');
          startRecorderFallback();
          return;
        }
        setSpeechError(friendly);
        setIsListening(false);
        setInterimTranscript('');
        setRecordingMode(null);
      },
      onEnd: () => {
        if (shouldKeepListeningRef.current && !isEvaluatingRef.current) {
          // Speech recognizers stop on silence — auto-restart seamlessly
          window.setTimeout(() => {
            if (shouldKeepListeningRef.current) {
              startListening();
            }
          }, 250);
        } else if (recordingModeRef.current !== 'recorder') {
          setIsListening(false);
          setInterimTranscript('');
          setRecordingMode(null);
        }
      }
    });

    if (!recognizer) {
      shouldKeepListeningRef.current = false;
      // No Web Speech support — use recorder fallback directly
      setIsListening(false);
      setInterimTranscript('');
      startRecorderFallback();
      return;
    }

    recognitionRef.current = recognizer;
    try {
      recognizer.start();
      setIsListening(true);
    } catch (e) {
      console.warn('Speech recognition start failed:', e);
      shouldKeepListeningRef.current = false;
      setIsListening(false);
      setIsSpeaking(false);
      startRecorderFallback();
    }
  };

  // Fallback mode: record mic locally, transcribe via server (Groq Whisper)
  const startRecorderFallback = async () => {
    recordingModeRef.current = 'recorder';
    setRecordingMode('recorder');
    setIsTranscribing(false);
    setRecordingSeconds(0);
    setIsListening(true);
    setSpeechError(
      'Chrome\'s built-in speech service is unreachable — using secure server transcription (Groq Whisper) instead.'
    );

    if (!isAudioRecordingSupported()) {
      recordingModeRef.current = null;
      setRecordingMode(null);
      setIsListening(false);
      setMicSupported(false);
      setSpeechError('Voice input is not supported in this browser. Please type your answer.');
      return;
    }

    try {
      const recorder = await createAudioRecorder();
      if (!recorder) {
        throw new Error('recorder-unavailable');
      }
      recorderRef.current = recorder;
      recordingTimerRef.current = setInterval(() => {
        setRecordingSeconds(s => s + 1);
      }, 1000);
    } catch (e: any) {
      console.warn('getUserMedia failed:', e);
      recordingModeRef.current = null;
      setRecordingMode(null);
      setIsListening(false);
      const name = e?.name || '';
      if (name === 'NotAllowedError' || name === 'SecurityError') {
        setSpeechError('Microphone access was denied. Allow microphone permission and try again.');
      } else if (name === 'NotFoundError' || name === 'OverconstrainedError' || e?.message === 'recorder-unavailable') {
        setSpeechError('No microphone was detected. Connect a microphone and try again.');
      } else {
        setSpeechError('Could not access the microphone. Please check your microphone and browser permissions.');
      }
    }
  };

  const stopRecorderFallback = async () => {
    recordingModeRef.current = null;
    setRecordingMode(null);
    setIsListening(false);

    const handle = recorderRef.current;
    stopActiveRecorder();
    if (!handle) return;

    setIsTranscribing(true);
    setSpeechError(null);
    try {
      const { blob, mimeType } = await handle.stop();
      const text = await transcribeAudio(blob, mimeType);
      if (text.trim()) {
        setUserAnswer(prev => prev ? `${prev} ${text.trim()}` : text.trim());
      } else {
        setSpeechError('No speech was detected in the recording. Please try again.');
      }
    } catch (e: any) {
      console.warn('Transcription failed:', e);
      setSpeechError(e?.message || 'Transcription failed. Please try again or type your answer.');
    } finally {
      setIsTranscribing(false);
    }
  };

  // Handle Speech Recognition Dictation
  const toggleVoiceRecording = () => {
    if (isListening || isTranscribing) {
      // Stop whatever mode is active
      shouldKeepListeningRef.current = false;
      if (recordingMode === 'recorder') {
        stopRecorderFallback();
      } else {
        if (recognitionRef.current) {
          try {
            recognitionRef.current.stop();
          } catch {
            // ignore
          }
        }
        setIsListening(false);
        setInterimTranscript('');
        setRecordingMode(null);
      }
      return;
    }

    shouldKeepListeningRef.current = true;
    setRecordingMode('wsapi');
    startListening();
  };

  const stopVoiceRecording = () => {
    shouldKeepListeningRef.current = false;
    if (recordingMode === 'recorder') {
      stopRecorderFallback();
      return;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
    }
    setIsListening(false);
    setInterimTranscript('');
    setRecordingMode(null);
  };

  // Insert STAR behavioral template helper
  const insertStarTemplate = () => {
    const template = `**Situation:**\n\n**Task:**\n\n**Action:**\n\n**Result & Metrics:**\n`;
    setUserAnswer(prev => prev ? `${prev}\n\n${template}` : template);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userAnswer.trim() || isEvaluating || isFinishingInterview) return;
    if (isTranscribing) return;
    // If recording via the server fallback, stop first and wait for the
    // transcript to land instead of submitting a partial answer.
    if (isListening && recordingMode === 'recorder') {
      stopRecorderFallback();
      return;
    }
    stopSpeaking();
    setIsSpeaking(false);
    stopVoiceRecording();
    onEvaluateAnswer(userAnswer.trim());
  };

  // Keyboard shortcut: Ctrl/Cmd + Enter to submit, Esc to stop dictation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (userAnswer.trim() && !isEvaluating && !isTranscribing && !isListening) {
          handleSubmit(e as unknown as React.FormEvent);
        }
      }
      if (e.key === 'Escape' && isListening) {
        stopVoiceRecording();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [userAnswer, isEvaluating, isListening, isTranscribing, recordingMode, isFinishingInterview]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatRecordingTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Live word-count guidance for a well-structured answer
  const wordCount = userAnswer.trim().split(/\s+/).filter(Boolean).length;
  const wordStatus = wordCount === 0
    ? null
    : wordCount < 60
    ? { label: 'Too brief — expand with structure & specific detail', tone: 'text-amber-400', dot: 'bg-amber-400' }
    : wordCount <= 200
    ? { label: 'Good response length', tone: 'text-emerald-400', dot: 'bg-emerald-400' }
    : { label: 'Very detailed — keep it focused & concise', tone: 'text-indigo-400', dot: 'bg-indigo-400' };

  const isLastQuestion = turnIndex + 1 >= totalTurns;
  const evaluation = currentTurn.evaluation;

  // Verdict badge colors
  const getVerdictBadge = (verdict: AnswerEvaluation['verdict']) => {
    switch (verdict) {
      case 'Strong Hire':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50';
      case 'Hire':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
      case 'Leaning Hire':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
      default:
        return 'bg-rose-500/20 text-rose-300 border-rose-500/50';
    }
  };

  return (
    <div id="active-interview-container" className="w-full max-w-5xl mx-auto space-y-6">
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="text-2xl">{activePersona.avatar}</div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white">{activePersona.name}</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                {activePersona.badge}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Role: <strong className="text-slate-200">{roleTitle}</strong> ({config.seniority.toUpperCase()})
              {config.companyTarget && ` • ${config.companyTarget}`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Question Counter & Progress */}
          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono">
              Question <strong className="text-white text-sm">{turnIndex + 1}</strong> of <strong className="text-slate-300">{totalTurns}</strong>
            </div>
            <div className="w-32 h-1.5 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
                style={{ width: `${((turnIndex + 1) / totalTurns) * 100}%` }}
              />
            </div>
          </div>

          {/* Question Stopwatch */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>{formatTimer(elapsedSeconds)}</span>
            <button
              id="toggle-interview-timer-btn"
              onClick={() => setIsTimerRunning(!isTimerRunning)}
              className="p-1 text-slate-400 hover:text-white"
              title={isTimerRunning ? "Pause timer" : "Resume timer"}
            >
              {isTimerRunning ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            </button>
          </div>

          <button
            id="exit-interview-btn"
            onClick={onCancelInterview}
            className="text-xs text-slate-500 hover:text-rose-400 transition-colors"
          >
            End Early
          </button>
        </div>
      </div>

      {/* Main Question Card */}
      <motion.div
        key={`question-${currentTurn.questionNumber}`}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/30 border border-slate-700/70 shadow-xl space-y-4 relative"
      >
        {/* Category & Difficulty Badges */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
              {currentTurn.category}
            </span>
            <span className={`text-[11px] font-mono px-2 py-0.5 rounded-md ${
              currentTurn.difficulty === 'Deep Dive' 
                ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30' 
                : currentTurn.difficulty === 'Challenging'
                ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
            }`}>
              {currentTurn.difficulty}
            </span>
          </div>

          {/* TTS Audio Readout */}
          <button
            id="tts-question-btn"
            onClick={toggleTTS}
            className={`p-2 rounded-xl border text-xs flex items-center gap-1.5 transition-all ${
              isSpeaking
                ? 'bg-indigo-600 text-white border-indigo-500 shadow-md animate-pulse'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white hover:bg-slate-700'
            }`}
            title="Listen to interviewer voice"
          >
            {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            <span className="font-mono text-[11px]">{isSpeaking ? 'Mute' : 'Listen'}</span>
          </button>
        </div>

        {/* Question Text */}
        <div className="space-y-1">
          <h2 className="text-lg sm:text-xl font-semibold text-white leading-relaxed">
            {currentTurn.question}
          </h2>
        </div>

        {/* Optional Context / Hint Accordion */}
        {currentTurn.contextTip && (
          <div>
            <button
              id="toggle-hint-btn"
              onClick={() => setShowTip(!showTip)}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 transition-colors font-medium"
            >
              <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
              <span>{showTip ? 'Hide Interviewer Context & Hint' : 'What is the interviewer looking for? (Hint)'}</span>
            </button>
            <AnimatePresence>
              {showTip && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden mt-2"
                >
                  <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300 leading-relaxed font-sans">
                    <strong className="text-amber-300">Focus Areas:</strong> {currentTurn.contextTip}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

      {/* Answer Area or Evaluation Feedback */}
      {!evaluation ? (
        /* Answer Input Phase */
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <MessageSquare className="w-4 h-4 text-indigo-400" />
              <span>Your Spoken or Written Response</span>
            </div>

            <div className="flex items-center gap-2">
              {/* STAR Framework shortcut for behavioral */}
              <button
                id="insert-star-btn"
                onClick={insertStarTemplate}
                disabled={isListening || isEvaluating}
                className="px-2.5 py-1.5 rounded-xl text-xs bg-slate-800 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600 transition-colors flex items-center gap-1 disabled:opacity-40 disabled:cursor-not-allowed"
                title="Insert STAR Framework Structure"
              >
                <ListOrdered className="w-3.5 h-3.5 text-purple-400" />
                <span className="hidden sm:inline">Insert STAR Template</span>
              </button>

              {/* Voice Dictation Button */}
              <button
                id="voice-dictation-btn"
                onClick={toggleVoiceRecording}
                disabled={!micSupported || isEvaluating || isTranscribing}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium border flex items-center gap-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed ${
                  isListening
                    ? 'bg-rose-500 text-white border-rose-400 shadow-lg shadow-rose-500/30'
                    : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white hover:bg-slate-700'
                }`}
                title="Dictate with microphone"
              >
                {isTranscribing ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Transcribing...</span>
                  </>
                ) : isListening ? (
                  <Mic className="w-3.5 h-3.5 animate-pulse" />
                ) : (
                  <MicOff className="w-3.5 h-3.5 text-slate-400" />
                )}
                <span>
                  {isTranscribing
                    ? 'Processing...'
                    : isListening
                    ? recordingMode === 'recorder'
                      ? 'Stop Recording'
                      : 'Stop Dictation'
                    : 'Voice Input'}
                </span>
              </button>
            </div>
          </div>

          {speechError && (
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <span>{speechError}</span>
            </div>
          )}

          {/* Server-side transcription spinner */}
          <AnimatePresence>
            {isTranscribing && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/40 flex items-center gap-3">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin shrink-0" />
                  <span className="text-xs text-indigo-200">
                    Transcribing your recording with secure server speech-to-text (Groq Whisper)...
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Live Dictation Panel */}
          <AnimatePresence>
            {isListening && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 flex items-start gap-3">
                  <div className="p-2 rounded-xl bg-rose-500/20 border border-rose-500/30 shrink-0">
                    {recordingMode === 'recorder' ? (
                      <span className="block w-3 h-3 rounded-full bg-rose-400 animate-pulse" />
                    ) : (
                      <AudioLines className="w-5 h-5 text-rose-300" />
                    )}
                  </div>
                  <div className="flex-1 space-y-1.5 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      {recordingMode === 'recorder' ? (
                        <span className="text-xs font-semibold text-rose-200 flex items-center gap-2 font-mono">
                          <span className="inline-block w-2 h-2 rounded-full bg-rose-400 animate-pulse" />
                          Recording {formatRecordingTimer(recordingSeconds)} — press Stop when done
                        </span>
                      ) : (
                        <span className="text-xs font-semibold text-rose-200 flex items-center gap-2">
                          <span className="flex items-end gap-0.5 h-4">
                            {[0, 1, 2, 3, 4, 5].map(i => (
                              <span
                                key={i}
                                className="mic-eq-bar w-1 rounded-full bg-rose-400"
                                style={{ height: '100%', animationDelay: `${i * 0.12}s` }}
                              />
                            ))}
                          </span>
                          Listening — speak your answer naturally
                        </span>
                      )}
                      <button
                        id="stop-dictation-btn"
                        onClick={stopVoiceRecording}
                        disabled={isTranscribing}
                        className="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-200 hover:bg-rose-500/40 text-[11px] font-semibold border border-rose-500/40 flex items-center gap-1 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        <Square className="w-3 h-3" />
                        Stop
                      </button>
                    </div>
                    <div className="min-h-[28px]">
                      {recordingMode === 'recorder' ? (
                        <p className="text-xs text-rose-300/60 italic">
                          Your words will appear here after you stop and they are transcribed.
                        </p>
                      ) : interimTranscript ? (
                        <p className="text-sm text-rose-100 leading-relaxed">
                          <span className="text-rose-300/90">{interimTranscript}</span>
                          <span className="dictation-caret text-rose-400">|</span>
                        </p>
                      ) : (
                        <p className="text-xs text-rose-300/60 italic">Waiting for your voice...</p>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Main Answer Textarea */}
          <div className="relative">
            <textarea
              id="candidate-answer-textarea"
              ref={textareaRef}
              rows={7}
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              disabled={isListening || isTranscribing}
              placeholder={`Structure your answer clearly. Explain trade-offs, architecture decisions, failure modes, or STAR stories...\n\n(Tip: Press the 'Voice Input' button and speak your answer naturally)`}
              className={`w-full p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-sans leading-relaxed resize-y ${
                isListening ? 'border-rose-500/50 bg-slate-800/50' : ''
              }`}
            />
          </div>

          {/* Word Count & Submit Actions */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
            <div className="text-xs font-mono space-y-1">
              <div className="flex flex-wrap items-center gap-1.5 text-slate-500">
                <span>{wordCount} words</span>
                <span className="mx-1">•</span>
                <span>~{(wordCount / 130).toFixed(1)} mins speaking</span>
                {wordStatus && (
                  <>
                    <span className="mx-1">•</span>
                    <span className={`flex items-center gap-1.5 ${wordStatus.tone}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${wordStatus.dot}`} />
                      {wordStatus.label}
                    </span>
                  </>
                )}
              </div>
              <div className="text-[11px] text-slate-600 flex items-center gap-1">
                <Command className="w-3 h-3" />
                <span className="flex items-center gap-0.5">
                  Ctrl/Cmd
                  <span className="px-1 rounded bg-slate-800 border border-slate-700 text-slate-400">Enter</span>
                </span>
                <span className="mx-1">to submit</span>
                <span className="text-slate-700">•</span>
                <span className="flex items-center gap-0.5">
                  <span className="px-1 rounded bg-slate-800 border border-slate-700 text-slate-400">Esc</span>
                </span>
                <span>to stop dictation</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {userAnswer && (
                <button
                  id="clear-answer-btn"
                  onClick={() => setUserAnswer('')}
                  disabled={isListening || isTranscribing}
                  className="px-3 py-2 text-xs text-slate-400 hover:text-slate-200 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Clear
                </button>
              )}

              <button
                id="submit-answer-btn"
                disabled={!userAnswer.trim() || isEvaluating || isFinishingInterview || isTranscribing}
                onClick={handleSubmit}
                className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all active:scale-[0.99] cursor-pointer"
              >
                {isEvaluating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>{activePersona.name} is evaluating...</span>
                  </>
                ) : (
                  <>
                    <span>Submit for Evaluation</span>
                    <Send className="w-3.5 h-3.5" />
                    <CornerDownLeft className="w-3 h-3 text-indigo-300 hidden sm:block" />
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.div>
      ) : (
        /* Evaluation & Feedback Phase */
        <motion.div
          id="evaluation-feedback-card"
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-6"
        >
          {/* Verdict & Score Banner */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-900/60 to-purple-900/60 border border-indigo-500/40 text-center">
                  <div>
                    <div className="text-2xl font-bold font-mono text-white leading-none">{evaluation.score}</div>
                    <div className="text-[10px] text-indigo-300 font-mono">/ 100</div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-400">Round Verdict:</span>
                    <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getVerdictBadge(evaluation.verdict)}`}>
                      {evaluation.verdict}
                    </span>
                  </div>
                  <h3 className="text-base font-semibold text-white mt-1">
                    {evaluation.score >= 85 ? 'Outstanding Response' : evaluation.score >= 70 ? 'Solid Technical Baseline' : 'Needs Substantive Refinement'}
                  </h3>
                </div>
              </div>

              {/* Spoken Quote Card */}
              <div className="max-w-md p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-start gap-3">
                <span className="text-xl shrink-0">{activePersona.avatar}</span>
                <div className="space-y-0.5">
                  <div className="text-[11px] font-bold text-slate-300">{activePersona.name} ({activePersona.badge})</div>
                  <p className="text-xs text-slate-400 italic leading-relaxed">"{evaluation.interviewerComment}"</p>
                </div>
              </div>
            </div>

            {/* 4 Standardized Metric Bars */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Technical Accuracy', score: evaluation.metrics?.technicalAccuracy ?? evaluation.score },
                { label: 'Clarity & Structure', score: evaluation.metrics?.clarityAndStructure ?? evaluation.score },
                { label: 'Depth & Relevance', score: evaluation.metrics?.depthAndRelevance ?? evaluation.score },
                { label: 'Problem Solving / STAR', score: evaluation.metrics?.problemSolvingOrSTAR ?? evaluation.score },
              ].map((metric) => (
                <div key={metric.label} className="p-3 rounded-xl bg-slate-800/40 border border-slate-800">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="text-slate-400">{metric.label}</span>
                    <span className="font-mono font-bold text-white">{metric.score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        metric.score >= 80 ? 'bg-emerald-500' : metric.score >= 65 ? 'bg-indigo-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${metric.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Strengths & Growth Areas Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Strengths */}
              <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Key Strengths Observed</span>
                </div>
                <ul className="text-xs text-slate-300 space-y-1.5 pl-4 list-disc">
                  {evaluation.strengths.map((str, idx) => (
                    <li key={idx} className="leading-relaxed">{str}</li>
                  ))}
                </ul>
              </div>

              {/* Areas for Improvement */}
              <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-amber-400">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Growth Areas & Refinements</span>
                </div>
                <ul className="text-xs text-slate-300 space-y-1.5 pl-4 list-disc">
                  {evaluation.areasForImprovement.map((area, idx) => (
                    <li key={idx} className="leading-relaxed">{area}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Missed Key Points */}
            {evaluation.missedKeyPoints?.length > 0 && (
              <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
                  <Lightbulb className="w-4 h-4" />
                  <span>Critical Points & Edge Cases to Mention (FAANG Caliber)</span>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  {evaluation.missedKeyPoints.map((point, idx) => (
                    <span key={idx} className="text-xs px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                      • {point}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Exemplary Answer Accordion */}
            {evaluation.exemplaryAnswer && (
              <div className="space-y-2">
                <button
                  id="toggle-exemplary-answer-btn"
                  onClick={() => setShowExemplary(!showExemplary)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 transition-colors font-semibold"
                >
                  <BookOpen className="w-4 h-4 text-indigo-400" />
                  <span>{showExemplary ? 'Hide Staff-Level Model Benchmark Answer' : 'View Staff-Level Model Benchmark Answer (How a top 1% engineer answers)'}</span>
                </button>
                <AnimatePresence>
                  {showExemplary && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 rounded-xl bg-slate-800/80 border border-indigo-500/30 text-xs text-slate-200 leading-relaxed font-mono whitespace-pre-wrap">
                        {evaluation.exemplaryAnswer}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {/* Next Action Button */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              {isLastQuestion ? (
                <button
                  id="view-final-report-btn"
                  onClick={onFinishInterview}
                  disabled={isFinishingInterview}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-lg shadow-emerald-600/30 flex items-center gap-2 transition-all active:scale-[0.99] cursor-pointer"
                >
                  {isFinishingInterview ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Compiling Final Scorecard & 4-Week Plan...</span>
                    </>
                  ) : (
                    <>
                      <Award className="w-4 h-4" />
                      <span>Generate Final Hiring Scorecard & Study Plan</span>
                    </>
                  )}
                </button>
              ) : (
                <button
                  id="next-question-btn"
                  onClick={onProceedToNextQuestion}
                  className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all active:scale-[0.99] cursor-pointer"
                >
                  <span>Proceed to Question {turnIndex + 2} of {totalTurns}</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};
