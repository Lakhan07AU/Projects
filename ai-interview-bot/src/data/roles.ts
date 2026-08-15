import { RolePreset } from '../types';

export const ROLE_PRESETS: RolePreset[] = [
  {
    id: 'frontend_engineer',
    title: 'Frontend Engineer',
    category: 'engineering',
    description: 'Modern Web Apps, React, Next.js, Performance Optimization, TypeScript, State Management, Web APIs',
    iconName: 'Layout',
    suggestedSkills: ['React', 'TypeScript', 'Tailwind CSS', 'Next.js', 'Web Vitals', 'State Management', 'Browser Rendering Engine'],
    sampleQuestions: [
      'How does React reconcile virtual DOM changes in React 18/19 with Concurrent Mode and Fiber architecture?',
      'Explain your strategy for reducing First Contentful Paint (FCP) and Largest Contentful Paint (LCP) in a heavy single-page application.',
      'How would you design a real-time collaborative rich-text editor with conflict resolution?'
    ]
  },
  {
    id: 'backend_engineer',
    title: 'Backend / Distributed Systems Engineer',
    category: 'engineering',
    description: 'Microservices, High Throughput APIs, Database Design, Caching, Concurrency, Message Queues',
    iconName: 'Server',
    suggestedSkills: ['Node.js', 'Go / Python', 'PostgreSQL', 'Redis', 'Kafka', 'Distributed Systems', 'gRPC'],
    sampleQuestions: [
      'How would you handle race conditions and prevent double-spending in a distributed payment ledger?',
      'Explain the trade-offs between optimistic locking and pessimistic locking under high write contention.',
      'How do you design a rate limiter that scales horizontally across multiple data centers with Redis?'
    ]
  },
  {
    id: 'fullstack_engineer',
    title: 'Full Stack Engineer',
    category: 'engineering',
    description: 'End-to-end architecture, Client-Server communication, API Design, Auth, Cloud deployment',
    iconName: 'Layers',
    suggestedSkills: ['React', 'TypeScript', 'Node.js', 'SQL/NoSQL', 'REST / GraphQL', 'Authentication / OAuth', 'Docker'],
    sampleQuestions: [
      'Walk me through the end-to-end flow of securing authentication with JWTs, refresh tokens, and HttpOnly cookies.',
      'How do you balance server-side rendering (SSR) vs client-side rendering (CSR) for an interactive analytics dashboard?',
      'Describe a scenario where you had to debug a subtle memory leak spanning both frontend and backend.'
    ]
  },
  {
    id: 'ai_ml_engineer',
    title: 'AI / Machine Learning Engineer',
    category: 'ai_data',
    description: 'LLM Systems, RAG Pipelines, Vector Databases, Fine-tuning, Model Serving, Evaluation Metrics',
    iconName: 'BrainCircuit',
    suggestedSkills: ['LLM Architectures', 'RAG', 'Vector DBs (Pinecone/Milvus)', 'Python', 'PyTorch', 'Prompt Engineering', 'LangChain/LlamaIndex'],
    sampleQuestions: [
      'How do you design an enterprise RAG system that minimizes hallucinations and handles stale document indexing?',
      'What evaluation metrics and benchmark frameworks would you set up to evaluate LLM output quality in production?',
      'Explain quantization techniques (GGUF, AWQ, GPTQ) and their trade-offs in inference latency vs model accuracy.'
    ]
  },
  {
    id: 'devops_cloud',
    title: 'DevOps / Cloud Platform & SRE',
    category: 'operations',
    description: 'Kubernetes, CI/CD, Infrastructure as Code, Cloud Architecture (GCP/AWS), Observability',
    iconName: 'CloudCog',
    suggestedSkills: ['Kubernetes', 'Docker', 'Terraform', 'CI/CD Pipelines', 'Prometheus & Grafana', 'AWS / GCP', 'Site Reliability Engineering'],
    sampleQuestions: [
      'How do you architect a zero-downtime blue-green deployment strategy for a Kubernetes cluster running mission-critical workloads?',
      'Walk through how you investigate and mitigate a cascading outage caused by a slow database dependency.',
      'How do you manage secrets and IAM least-privilege policies across multi-tenant cloud environments?'
    ]
  },
  {
    id: 'product_manager',
    title: 'Product Manager (Technical & Growth)',
    category: 'product_design',
    description: 'Product Strategy, User Research, Feature Prioritization, Metrics Definition (North Star), Roadmap Execution',
    iconName: 'Compass',
    suggestedSkills: ['Product Strategy', 'A/B Testing', 'User Journeys', 'Data Analytics', 'Agile Roadmapping', 'Stakeholder Management'],
    sampleQuestions: [
      'How would you define the North Star metric for an AI-powered search tool, and what guardrail metrics would you track?',
      'Tell me about a time you had to kill a feature that engineering spent months building. How did you handle stakeholder alignment?',
      'If active user retention dropped 15% following a major mobile redesign, how would you systematically diagnose the root cause?'
    ]
  },
  {
    id: 'data_scientist',
    title: 'Data Scientist & Analytics Lead',
    category: 'ai_data',
    description: 'Statistical Inference, Predictive Modeling, SQL/Data Warehousing, Experimentation, Business Insights',
    iconName: 'BarChart3',
    suggestedSkills: ['SQL', 'Python / R', 'A/B Experimentation', 'Pandas / NumPy', 'Statistical Modeling', 'Tableau / Looker'],
    sampleQuestions: [
      'How do you handle covariate shift and sample ratio mismatch (SRM) in online A/B experimentation?',
      'Explain how you would build a churn prediction model and translate its probabilities into an actionable business retention campaign.',
      'What are the core differences between Random Forests and Gradient Boosted Trees in terms of bias-variance trade-offs?'
    ]
  },
  {
    id: 'system_architect',
    title: 'Staff / Principal System Architect',
    category: 'engineering',
    description: 'Large-scale system design, High Availability, Fault Tolerance, Event-driven Architectures, CAP Theorem',
    iconName: 'Network',
    suggestedSkills: ['System Design', 'Event-Driven Architecture', 'CAP Theorem', 'Fault Tolerance', 'Multi-Region Replication', 'Cost Optimization'],
    sampleQuestions: [
      'Design a global URL shortening and analytics service handling 100,000 writes/second and 1,000,000 reads/second with <10ms latency.',
      'How do you handle data consistency and distributed transactions across microservices without introducing distributed locks?',
      'How would you migrate a monolithic database with 50TB of data to a sharded database with zero read/write downtime?'
    ]
  }
];

export const PERSONA_PROFILES = [
  {
    id: 'faang_strict' as const,
    name: 'Alex Vance',
    title: 'Staff Bar Raiser (FAANG / Tier-1)',
    tone: 'Rigorous, deeply technical, probes edge cases and scalability limits',
    avatar: '👨‍💼',
    badge: 'FAANG Standard',
    accentColor: 'border-blue-500/40 bg-blue-500/10 text-blue-400'
  },
  {
    id: 'encouraging_coach' as const,
    name: 'Jordan Reed',
    title: 'Senior Engineering Mentor',
    tone: 'Constructive, supportive, helps unblock reasoning, focuses on growth',
    avatar: '👩‍🏫',
    badge: 'Growth Coach',
    accentColor: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400'
  },
  {
    id: 'startup_cto' as const,
    name: 'Elena Rostova',
    title: 'Series-B Startup CTO',
    tone: 'Pragmatic, speed vs trade-offs focused, values ownership and execution',
    avatar: '🚀',
    badge: 'High Velocity',
    accentColor: 'border-amber-500/40 bg-amber-500/10 text-amber-400'
  },
  {
    id: 'behavioral_expert' as const,
    name: 'Dr. Marcus Hill',
    title: 'People & Leadership Specialist',
    tone: 'Deep focus on STAR format, conflict resolution, leadership, and emotional intelligence',
    avatar: '🎯',
    badge: 'Leadership & STAR',
    accentColor: 'border-purple-500/40 bg-purple-500/10 text-purple-400'
  }
];
