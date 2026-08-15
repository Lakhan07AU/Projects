import React, { useState } from 'react';
import { motion } from 'motion/react';
import { 
  Briefcase, 
  Sparkles, 
  Layers, 
  Server, 
  Layout, 
  BrainCircuit, 
  CloudCog, 
  Compass, 
  BarChart3, 
  Network, 
  ChevronRight, 
  Building2, 
  UserCheck, 
  HelpCircle,
  Clock,
  Plus
} from 'lucide-react';
import { InterviewConfig, SeniorityLevel, InterviewType, InterviewerPersona } from '../types';
import { ROLE_PRESETS, PERSONA_PROFILES } from '../data/roles';

interface RoleSelectorProps {
  onStartInterview: (config: InterviewConfig) => void;
  isLoading: boolean;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  Layout: <Layout className="w-5 h-5" />,
  Server: <Server className="w-5 h-5" />,
  Layers: <Layers className="w-5 h-5" />,
  BrainCircuit: <BrainCircuit className="w-5 h-5" />,
  CloudCog: <CloudCog className="w-5 h-5" />,
  Compass: <Compass className="w-5 h-5" />,
  BarChart3: <BarChart3 className="w-5 h-5" />,
  Network: <Network className="w-5 h-5" />,
};

const CATEGORIES = [
  { id: 'all', label: 'All Roles' },
  { id: 'engineering', label: 'Engineering' },
  { id: 'ai_data', label: 'AI & Data' },
  { id: 'product_design', label: 'Product & Design' },
  { id: 'operations', label: 'DevOps / SRE' },
];

const SENIORITIES: { id: SeniorityLevel; label: string; exp: string }[] = [
  { id: 'junior', label: 'Junior', exp: '0-2 Yrs' },
  { id: 'mid', label: 'Mid-Level', exp: '3-5 Yrs' },
  { id: 'senior', label: 'Senior', exp: '5-8 Yrs' },
  { id: 'staff', label: 'Staff / Lead', exp: '8+ Yrs' },
];

const INTERVIEW_TYPES: { id: InterviewType; label: string; desc: string }[] = [
  { id: 'mixed', label: 'Comprehensive Mixed', desc: 'Architecture, deep-dives & behavioral questions' },
  { id: 'technical', label: 'Deep Technical', desc: 'Core language internals, algorithms & performance' },
  { id: 'system_design', label: 'System Design', desc: 'Scalability, microservices, databases & latency' },
  { id: 'behavioral', label: 'Leadership & STAR', desc: 'Conflict resolution, ownership & high stakes' },
];

const COMPANIES = ['Google', 'Meta', 'Amazon', 'Apple', 'Stripe', 'Netflix', 'OpenAI', 'High-Growth Startup'];

export const RoleSelector: React.FC<RoleSelectorProps> = ({ onStartInterview, isLoading }) => {
  const [selectedCategoryId, setSelectedCategoryId] = useState('all');
  const [selectedRoleId, setSelectedRoleId] = useState<string>('frontend_engineer');
  const [isCustomRole, setIsCustomRole] = useState(false);
  const [customTitle, setCustomTitle] = useState('');
  const [seniority, setSeniority] = useState<SeniorityLevel>('senior');
  const [interviewType, setInterviewType] = useState<InterviewType>('mixed');
  const [persona, setPersona] = useState<InterviewerPersona>('faang_strict');
  const [totalQuestions, setTotalQuestions] = useState<number>(5);
  const [targetCompany, setTargetCompany] = useState<string>('Google');

  const filteredRoles = selectedCategoryId === 'all' 
    ? ROLE_PRESETS 
    : ROLE_PRESETS.filter(r => r.category === selectedCategoryId);

  const handleStart = () => {
    const finalRoleTitle = isCustomRole ? customTitle.trim() : undefined;
    if (isCustomRole && !customTitle.trim()) {
      return;
    }

    onStartInterview({
      roleId: isCustomRole ? 'custom' : selectedRoleId,
      customRoleTitle: finalRoleTitle,
      seniority,
      interviewType,
      interviewerPersona: persona,
      totalQuestions,
      companyTarget: targetCompany
    });
  };

  const currentRoleObj = ROLE_PRESETS.find(r => r.id === selectedRoleId);

  return (
    <div id="role-selector-container" className="w-full max-w-6xl mx-auto space-y-8">
      {/* Hero Intro */}
      <div className="text-center space-y-3 pt-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Next-Gen LLM Mock Interview Practice</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white">
          Master Your Next High-Stakes Tech Interview
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
          Simulate realistic, dynamic interviews with AI interviewer personas. Receive calibrated scoring rubrics, 
          exemplary answers, and a structured 4-week study plan.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Role Selection (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-indigo-400" />
              <h2 className="text-base font-semibold text-white">Step 1: Select Target Role</h2>
            </div>
            <button
              id="toggle-custom-role-btn"
              onClick={() => setIsCustomRole(!isCustomRole)}
              className={`text-xs px-2.5 py-1 rounded-lg border transition-all flex items-center gap-1.5 ${
                isCustomRole 
                  ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm' 
                  : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:border-slate-600'
              }`}
            >
              <Plus className="w-3 h-3" />
              <span>{isCustomRole ? 'Choose Preset Role' : 'Custom Job Title'}</span>
            </button>
          </div>

          {isCustomRole ? (
            <div id="custom-role-box" className="p-5 rounded-2xl bg-slate-900/90 border border-indigo-500/40 space-y-4">
              <label className="block text-xs font-semibold text-indigo-300 uppercase tracking-wider">
                Enter Custom Job Title / Specialty
              </label>
              <input
                id="custom-role-input"
                type="text"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="e.g. Rust Systems Engineer, iOS Swift Lead, Solidity Smart Contract Auditor..."
                className="w-full px-4 py-3 rounded-xl bg-slate-800/90 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <p className="text-xs text-slate-400">
                The LLM will tailor specific technical architecture, language nuances, and industry questions for this custom role.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Category Filter Pills */}
              <div className="flex flex-wrap gap-2">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    id={`category-filter-${cat.id}`}
                    onClick={() => setSelectedCategoryId(cat.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                      selectedCategoryId === cat.id
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                        : 'bg-slate-800/70 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>

              {/* Role Cards Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[380px] overflow-y-auto pr-1">
                {filteredRoles.map(role => {
                  const isSelected = selectedRoleId === role.id && !isCustomRole;
                  return (
                    <div
                      key={role.id}
                      id={`role-card-${role.id}`}
                      onClick={() => {
                        setSelectedRoleId(role.id);
                        setIsCustomRole(false);
                      }}
                      className={`p-4 rounded-xl border text-left cursor-pointer transition-all duration-200 flex flex-col justify-between ${
                        isSelected
                          ? 'bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500/50 shadow-lg shadow-indigo-950/50'
                          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40'
                      }`}
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className={`p-2 rounded-lg ${isSelected ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-400'}`}>
                            {ICON_MAP[role.iconName] || <Briefcase className="w-5 h-5" />}
                          </div>
                          {isSelected && (
                            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                              Selected
                            </span>
                          )}
                        </div>
                        <h3 className="font-semibold text-sm text-white line-clamp-1">{role.title}</h3>
                        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{role.description}</p>
                      </div>

                      <div className="flex flex-wrap gap-1 mt-3 pt-2 border-t border-slate-800/80">
                        {role.suggestedSkills.slice(0, 3).map(skill => (
                          <span key={skill} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Sample Questions Preview */}
          {!isCustomRole && currentRoleObj && (
            <div id="sample-questions-preview" className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
                <HelpCircle className="w-3.5 h-3.5" />
                <span>Representative Question Topics for {currentRoleObj.title}</span>
              </div>
              <ul className="text-xs text-slate-400 space-y-1.5 pl-4 list-disc">
                {currentRoleObj.sampleQuestions.map((q, idx) => (
                  <li key={idx} className="italic leading-relaxed">{q}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right Column: Calibration & Persona Setup (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-indigo-400" />
            <h2 className="text-base font-semibold text-white">Step 2: Configure Round & Persona</h2>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-5">
            {/* Seniority Level */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                <span>Experience Level</span>
                <span className="text-indigo-400 font-mono">{seniority.toUpperCase()}</span>
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {SENIORITIES.map(s => (
                  <button
                    key={s.id}
                    id={`seniority-btn-${s.id}`}
                    onClick={() => setSeniority(s.id)}
                    className={`py-2 px-1 rounded-xl text-center transition-all ${
                      seniority === s.id
                        ? 'bg-indigo-600 text-white font-medium shadow-sm'
                        : 'bg-slate-800/80 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="text-xs font-semibold">{s.label}</div>
                    <div className="text-[10px] text-slate-400/90 font-mono mt-0.5">{s.exp}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Interview Format */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Interview Focus Area
              </label>
              <div className="space-y-1.5">
                {INTERVIEW_TYPES.map(type => (
                  <div
                    key={type.id}
                    id={`type-option-${type.id}`}
                    onClick={() => setInterviewType(type.id)}
                    className={`p-2.5 rounded-xl border cursor-pointer transition-all flex items-start gap-3 ${
                      interviewType === type.id
                        ? 'bg-indigo-950/40 border-indigo-500/80 text-white'
                        : 'bg-slate-800/40 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="interview_type"
                      checked={interviewType === type.id}
                      onChange={() => setInterviewType(type.id)}
                      className="mt-1 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div>
                      <div className="text-xs font-semibold text-slate-200">{type.label}</div>
                      <div className="text-[11px] text-slate-400">{type.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Target Company */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                <span>Target Company Culture</span>
              </label>
              <div className="flex flex-wrap gap-1.5">
                {COMPANIES.map(company => (
                  <button
                    key={company}
                    id={`company-btn-${company.toLowerCase().replace(/\s+/g, '-')}`}
                    onClick={() => setTargetCompany(company)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                      targetCompany === company
                        ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/50'
                        : 'bg-slate-800/60 text-slate-400 hover:text-slate-300 border border-slate-700/40'
                    }`}
                  >
                    {company}
                  </button>
                ))}
              </div>
            </div>

            {/* Interviewer Persona */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                <span>Interviewer AI Persona</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {PERSONA_PROFILES.map(p => (
                  <div
                    key={p.id}
                    id={`persona-option-${p.id}`}
                    onClick={() => setPersona(p.id)}
                    className={`p-2.5 rounded-xl border cursor-pointer transition-all ${
                      persona === p.id
                        ? 'bg-indigo-950/60 border-indigo-500 ring-1 ring-indigo-500/40'
                        : 'bg-slate-800/40 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-base">{p.avatar}</span>
                      <span className="text-xs font-bold text-white leading-tight">{p.name}</span>
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono line-clamp-1">{p.badge}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Total Questions Counter */}
            <div className="space-y-2 pt-1 border-t border-slate-800">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-semibold flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  <span>Interview Length</span>
                </span>
                <span className="font-mono text-indigo-400 font-bold">{totalQuestions} Questions (~{totalQuestions * 3} mins)</span>
              </div>
              <div className="flex gap-2">
                {[3, 5, 7, 10].map(num => (
                  <button
                    key={num}
                    id={`questions-count-btn-${num}`}
                    onClick={() => setTotalQuestions(num)}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-mono transition-all ${
                      totalQuestions === num
                        ? 'bg-indigo-600 text-white font-bold'
                        : 'bg-slate-800/80 text-slate-400 hover:text-white'
                    }`}
                  >
                    {num} Qs
                  </button>
                ))}
              </div>
            </div>

            {/* Launch CTA */}
            <button
              id="start-mock-interview-btn"
              disabled={isLoading || (isCustomRole && !customTitle.trim())}
              onClick={handleStart}
              className="w-full mt-3 py-3.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all transform active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Generating Calibrated Question 1...</span>
                </>
              ) : (
                <>
                  <span>Begin Mock Interview</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
