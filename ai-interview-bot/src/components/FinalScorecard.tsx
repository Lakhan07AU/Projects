import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import confetti from 'canvas-confetti';
import { 
  Award, 
  CheckCircle2, 
  AlertTriangle, 
  Calendar, 
  Download, 
  Copy, 
  Check, 
  RotateCcw, 
  BookOpen, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  Star,
  Sparkles,
  UserCheck
} from 'lucide-react';
import { FinalReport, InterviewConfig, InterviewTurn } from '../types';
import { PERSONA_PROFILES, ROLE_PRESETS } from '../data/roles';

interface FinalScorecardProps {
  report: FinalReport;
  config: InterviewConfig;
  turns: InterviewTurn[];
  onRestart: () => void;
}

export const FinalScorecard: React.FC<FinalScorecardProps> = ({
  report,
  config,
  turns,
  onRestart,
}) => {
  const [copied, setCopied] = useState(false);
  const [expandedTurn, setExpandedTurn] = useState<number | null>(null);

  const activePersona = PERSONA_PROFILES.find(p => p.id === config.interviewerPersona) || PERSONA_PROFILES[0];
  const roleTitle = config.customRoleTitle || ROLE_PRESETS.find(r => r.id === config.roleId)?.title || config.roleId;

  // Trigger confetti on high hireability
  useEffect(() => {
    if (report.overallScore >= 75 || report.overallVerdict === 'Strong Hire' || report.overallVerdict === 'Hire') {
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (e) {
        // graceful ignore if canvas blocked
      }
    }
  }, [report]);

  // Copy full markdown report to clipboard
  const handleCopyMarkdown = () => {
    const md = `# AI Mock Interview Scorecard - ${roleTitle} (${config.seniority.toUpperCase()})
**Overall Score:** ${report.overallScore}/100
**Hiring Verdict:** ${report.overallVerdict}
**Interviewer:** ${activePersona.name} (${activePersona.badge})
**Date:** ${new Date().toLocaleDateString()}

## Executive Summary
${report.summaryAssessment}

## Competency Breakdown
${report.competencyBreakdown.map(c => `- **${c.category}:** ${c.score}/100 - ${c.summary}`).join('\n')}

## Top Strengths
${report.topStrengths.map(s => `- ${s}`).join('\n')}

## Critical Growth Areas
${report.topGrowthAreas.map(g => `- ${g}`).join('\n')}

## 4-Week Tailored Preparation Plan
${report.tailoredStudyPlan.map(p => `### ${p.week}: ${p.focus}\n${p.actionItems.map(a => `- [ ] ${a}`).join('\n')}`).join('\n\n')}

## Hiring Manager Notes
${report.hiringManagerNotes}

---
## Question Transcripts & Evaluations
${turns.map((t, idx) => `
### Question ${idx + 1}: ${t.question}
- **Category:** ${t.category} (${t.difficulty})
- **Candidate Answer:** ${t.userAnswer || 'N/A'}
- **Score:** ${t.evaluation?.score ?? 'N/A'}/100 (${t.evaluation?.verdict ?? 'N/A'})
- **Interviewer Feedback:** ${t.evaluation?.interviewerComment ?? 'N/A'}
`).join('\n')}
`;

    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({
      config,
      report,
      turns,
      generatedAt: new Date().toISOString()
    }, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `interview_scorecard_${config.roleId}_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getVerdictStyle = (verdict: FinalReport['overallVerdict']) => {
    switch (verdict) {
      case 'Strong Hire':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/60 ring-emerald-500/40';
      case 'Hire':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/60 ring-blue-500/40';
      case 'Leaning Hire':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/60 ring-amber-500/40';
      default:
        return 'bg-rose-500/20 text-rose-300 border-rose-500/60 ring-rose-500/40';
    }
  };

  return (
    <div id="final-scorecard-container" className="w-full max-w-5xl mx-auto space-y-8 pb-12">
      {/* Header Banner */}
      <div className="p-8 rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-700 shadow-2xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Comprehensive Interview Debrief</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">
              {roleTitle} Candidate Scorecard
            </h1>
            <p className="text-xs sm:text-sm text-slate-400">
              Evaluated by <strong className="text-slate-200">{activePersona.name}</strong> • {config.seniority.toUpperCase()} level
              {config.companyTarget && ` • ${config.companyTarget} Bar`}
            </p>
          </div>

          {/* Overall Score Dial */}
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-center justify-center w-24 h-24 rounded-2xl bg-slate-900 border border-indigo-500/50 shadow-lg text-center">
              <span className="text-3xl font-bold font-mono text-white leading-none">{report.overallScore}</span>
              <span className="text-xs text-indigo-400 font-mono mt-1">/ 100</span>
            </div>
            <div className="space-y-1">
              <span className="text-xs text-slate-400 font-mono block">Overall Recommendation:</span>
              <span className={`inline-block text-sm font-bold px-3 py-1 rounded-full border ring-1 ${getVerdictStyle(report.overallVerdict)}`}>
                {report.overallVerdict}
              </span>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="p-5 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Executive Performance Summary</span>
          </h3>
          <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
            {report.summaryAssessment}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <button
              id="copy-markdown-btn"
              onClick={handleCopyMarkdown}
              className="px-3.5 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors flex items-center gap-1.5"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied Markdown!' : 'Copy Markdown Report'}</span>
            </button>
            <button
              id="download-json-btn"
              onClick={handleDownloadJSON}
              className="px-3.5 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export JSON</span>
            </button>
          </div>

          <button
            id="restart-new-interview-btn"
            onClick={onRestart}
            className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Start New Interview</span>
          </button>
        </div>
      </div>

      {/* Competencies Breakdown */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <Star className="w-4 h-4 text-amber-400" />
          <span>Core Competency Rubric Scores</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {report.competencyBreakdown.map((comp, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-800/40 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-200">{comp.category}</span>
                <span className="font-mono text-xs font-bold text-indigo-300">{comp.score}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${comp.score >= 80 ? 'bg-emerald-500' : comp.score >= 65 ? 'bg-indigo-500' : 'bg-amber-500'}`}
                  style={{ width: `${comp.score}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">{comp.summary}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths vs Growth Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Strengths */}
        <div className="p-6 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>Demonstrated Strengths</span>
          </div>
          <ul className="text-xs text-slate-300 space-y-2 pl-4 list-disc">
            {report.topStrengths.map((str, idx) => (
              <li key={idx} className="leading-relaxed">{str}</li>
            ))}
          </ul>
        </div>

        {/* Top Growth Areas */}
        <div className="p-6 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-amber-400">
            <AlertTriangle className="w-4 h-4" />
            <span>Key Areas to Elevate</span>
          </div>
          <ul className="text-xs text-slate-300 space-y-2 pl-4 list-disc">
            {report.topGrowthAreas.map((growth, idx) => (
              <li key={idx} className="leading-relaxed">{growth}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* 4-Week Tailored Preparation Study Plan */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-400" />
            <div>
              <h3 className="text-sm font-semibold text-white">4-Week Personalized Mastery Roadmap</h3>
              <p className="text-xs text-slate-400">Targeted study topics and actionable drills based on your interview gaps</p>
            </div>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
            Action Plan
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {report.tailoredStudyPlan.map((plan, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-700/60">
                <span className="text-xs font-mono font-bold text-indigo-400">{plan.week}</span>
                <span className="text-xs font-semibold text-slate-200">{plan.focus}</span>
              </div>
              <ul className="text-xs text-slate-300 space-y-1.5 pl-4 list-disc">
                {plan.actionItems.map((item, itemIdx) => (
                  <li key={itemIdx} className="leading-relaxed">{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Hiring Manager Debrief Notes */}
      {report.hiringManagerNotes && (
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-indigo-500/30 flex items-start gap-4">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shrink-0">
            <UserCheck className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-indigo-300">Bar Raiser Hiring Decision Notes</h4>
            <p className="text-xs text-slate-300 leading-relaxed font-sans italic">
              "{report.hiringManagerNotes}"
            </p>
          </div>
        </div>
      )}

      {/* Question Transcripts Breakdown */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-indigo-400" />
          <span>Interview Questions & Responses Log</span>
        </h3>
        <div className="space-y-3">
          {turns.map((t, idx) => {
            const isExpanded = expandedTurn === idx;
            return (
              <div key={idx} className="rounded-xl border border-slate-800 bg-slate-800/30 overflow-hidden">
                <div
                  onClick={() => setExpandedTurn(isExpanded ? null : idx)}
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-800/60 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs font-bold text-indigo-400">Q{idx + 1}</span>
                    <span className="text-xs font-medium text-slate-200 line-clamp-1">{t.question}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {t.evaluation && (
                      <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                        {t.evaluation.score}/100
                      </span>
                    )}
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                  </div>
                </div>

                {isExpanded && (
                  <div className="p-4 pt-0 border-t border-slate-800/80 space-y-3 text-xs">
                    <div>
                      <strong className="text-slate-400 block mb-1">Your Answer:</strong>
                      <div className="p-3 rounded-lg bg-slate-900 text-slate-300 whitespace-pre-wrap font-sans">
                        {t.userAnswer || "No answer provided"}
                      </div>
                    </div>
                    {t.evaluation && (
                      <div>
                        <strong className="text-indigo-400 block mb-1">Interviewer Feedback:</strong>
                        <p className="text-slate-300 italic">"{t.evaluation.interviewerComment}"</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
