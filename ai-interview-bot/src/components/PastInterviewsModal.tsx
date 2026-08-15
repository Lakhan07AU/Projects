import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, History, Trash2, Calendar, Award, ChevronRight, FileText } from 'lucide-react';
import { SavedInterviewSession } from '../types';

interface PastInterviewsModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessions: SavedInterviewSession[];
  onSelectSession: (session: SavedInterviewSession) => void;
  onClearHistory: () => void;
}

export const PastInterviewsModal: React.FC<PastInterviewsModalProps> = ({
  isOpen,
  onClose,
  sessions,
  onSelectSession,
  onClearHistory,
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div
        id="past-interviews-backdrop"
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          id="past-interviews-dialog"
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-slate-900 border border-slate-700/80 rounded-2xl p-6 shadow-2xl text-slate-100 space-y-5"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
                <History className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Interview Practice History</h3>
                <p className="text-xs text-slate-400">Review your past scores and personalized study roadmaps</p>
              </div>
            </div>
            <button
              id="close-history-modal-btn"
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* List of sessions */}
          {sessions.length === 0 ? (
            <div className="text-center py-12 space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-800 text-slate-500 mx-auto flex items-center justify-center">
                <FileText className="w-6 h-6" />
              </div>
              <p className="text-sm text-slate-400">No mock interview sessions recorded yet.</p>
              <p className="text-xs text-slate-500">Complete your first mock interview to view historical analytics here.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((sess) => {
                const dateStr = new Date(sess.timestamp).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                });
                const roleTitle = sess.config.customRoleTitle || sess.config.roleId;
                const score = sess.report?.overallScore;
                const verdict = sess.report?.overallVerdict;

                return (
                  <div
                    key={sess.id}
                    id={`session-card-${sess.id}`}
                    onClick={() => onSelectSession(sess)}
                    className="p-4 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800/80 hover:border-slate-700 cursor-pointer transition-all flex items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-white">{roleTitle}</span>
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                          {sess.config.seniority}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-slate-500" />
                          {dateStr}
                        </span>
                        <span>•</span>
                        <span>{sess.turns.length} Questions</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {score !== undefined && (
                        <div className="text-right">
                          <div className="text-sm font-bold font-mono text-indigo-400">{score}/100</div>
                          {verdict && <div className="text-[10px] text-slate-400">{verdict}</div>}
                        </div>
                      )}
                      <ChevronRight className="w-4 h-4 text-slate-500" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Footer */}
          {sessions.length > 0 && (
            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <button
                id="clear-all-history-btn"
                onClick={onClearHistory}
                className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1.5 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear All History</span>
              </button>

              <button
                id="close-history-footer-btn"
                onClick={onClose}
                className="px-4 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200"
              >
                Close
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
