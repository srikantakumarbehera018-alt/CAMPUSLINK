// CAMPUSLINK – Frontend Application Controller

const API_BASE = '/api';

const state = {
    currentUser: null,
    token: localStorage.getItem('campuslink_token') || null,
    activeView: 'landing', // 'landing' | 'student' | 'recruiter' | 'admin'
    adminTab: 'overview',  // 'overview' | 'analytics' | 'drives' | 'pipeline' | 'offers' | 'documents' | 'atrisk'
    notifications: [],
    cachedStudents: [],
    cachedJobs: [],
    cachedDrives: [],
    selectedJobForMatching: 1,
    currentStudentId: null
};

// Toast Notifications Helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const bgColors = {
        success: 'bg-emerald-600 text-white',
        error: 'bg-rose-600 text-white',
        warning: 'bg-amber-600 text-white',
        info: 'bg-indigo-600 text-white'
    };
    toast.className = `px-4 py-3 rounded-xl shadow-lg text-xs font-semibold flex items-center space-x-2 transition-all duration-300 transform translate-y-2 pointer-events-auto ${bgColors[type] || bgColors.info}`;
    toast.innerHTML = `<span>${type === 'success' ? '✓' : (type === 'error' ? '✗' : 'ℹ')}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.remove('translate-y-2'), 10);
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// API Fetch Helper with Auth Header
async function api(endpoint, options = {}) {
    const headers = options.headers || {};
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    }
    options.headers = headers;
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        if (res.status === 401) {
            logout();
            throw new Error("Session expired. Please log in again.");
        }
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || data.message || "An error occurred");
        }
        return data;
    } catch (err) {
        console.error(`API Error [${endpoint}]:`, err);
        throw err;
    }
}

// App Initialization
document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();
    await checkAuth();
    if (!state.currentUser) {
        navigateTo('landing');
    }
});

async function checkAuth() {
    if (!state.token) {
        state.currentUser = null;
        updateNavAuth();
        return;
    }
    try {
        const user = await api('/auth/me');
        state.currentUser = user;
        updateNavAuth();
        fetchNotifications();
        if (user.role === 'STUDENT') {
            state.currentStudentId = user.profile_id || 1;
            navigateTo('student');
        } else if (user.role === 'RECRUITER') {
            navigateTo('recruiter');
        } else if (user.role === 'TPO_ADMIN') {
            navigateTo('admin');
        }
    } catch (e) {
        state.currentUser = null;
        state.token = null;
        localStorage.removeItem('campuslink_token');
        updateNavAuth();
        navigateTo('landing');
    }
}

function updateNavAuth() {
    const roleBadge = document.getElementById('nav-role-badge');
    const userLabel = document.getElementById('nav-user-label');
    const authActions = document.getElementById('auth-actions');
    const notifWrapper = document.getElementById('notif-wrapper');
    const authBtnContainer = document.getElementById('nav-auth-btn-container');

    if (state.currentUser) {
        roleBadge.classList.remove('hidden');
        userLabel.textContent = `${state.currentUser.name} (${state.currentUser.role})`;
        notifWrapper.classList.remove('hidden');

        // Navigation switcher buttons
        authActions.innerHTML = `
            ${state.currentUser.role === 'STUDENT' ? `<button onclick="navigateTo('student')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition">My Dashboard</button>` : ''}
            ${state.currentUser.role === 'RECRUITER' ? `<button onclick="navigateTo('recruiter')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-teal-50 text-teal-700 hover:bg-teal-100 transition">Recruiter Arena</button>` : ''}
            ${state.currentUser.role === 'TPO_ADMIN' ? `<button onclick="navigateTo('admin')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 transition">TPO Command</button>` : ''}
        `;

        authBtnContainer.innerHTML = `
            <button onclick="logout()" class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 transition">
                Logout
            </button>
        `;
    } else {
        roleBadge.classList.add('hidden');
        authActions.innerHTML = '';
        notifWrapper.classList.add('hidden');
        authBtnContainer.innerHTML = `
            <button onclick="openLoginModal()" class="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition">
                Login
            </button>
        `;
    }
    lucide.createIcons();
}

function navigateTo(view) {
    state.activeView = view;
    const content = document.getElementById('app-content');
    if (view === 'landing') {
        renderLandingView(content);
    } else if (view === 'student') {
        renderStudentDashboard(content, state.currentStudentId || 1);
    } else if (view === 'recruiter') {
        renderRecruiterDashboard(content);
    } else if (view === 'admin') {
        renderAdminDashboard(content);
    }
    lucide.createIcons();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// -------------------------------------------------------------------------------------------------
// 1. LANDING VIEW
// -------------------------------------------------------------------------------------------------
function renderLandingView(container) {
    container.innerHTML = `
        <!-- Hero Section -->
        <section class="relative overflow-hidden pt-12 pb-20 bg-gradient-to-b from-indigo-50/50 via-white to-slate-50 border-b border-slate-200/60">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
                <div class="text-center max-w-3xl mx-auto">
                    <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 mb-6 border border-indigo-200">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-600"></i>
                        <span>AI-Powered Campus-to-Corporate Placement Management</span>
                    </div>
                    <h1 class="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-slate-900 tracking-tight leading-tight">
                        From Campus Readiness to <span class="bg-gradient-to-r from-indigo-600 to-cyan-500 bg-clip-text text-transparent">Corporate Success</span>.
                    </h1>
                    <p class="mt-5 text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
                        One centralized, intelligent ecosystem replacing spreadsheets, email chains, and WhatsApp chaos. Powered by hybrid NLP matching, explainable readiness profiling, and automated conflict-free drive scheduling.
                    </p>

                    <!-- Primary CTAs -->
                    <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
                        <button onclick="loginAsPersona('rahul@campuslink.edu')" class="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-lg shadow-indigo-600/25 transition flex items-center space-x-2">
                            <span>🎓 Student Portal</span>
                            <i data-lucide="arrow-right" class="w-4 h-4"></i>
                        </button>
                        <button onclick="loginAsPersona('recruiter@technova.com')" class="px-5 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-lg shadow-teal-600/25 transition flex items-center space-x-2">
                            <span>🏢 Recruiter Portal</span>
                        </button>
                        <button onclick="loginAsPersona('tpo@campuslink.edu')" class="px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-semibold text-sm shadow-lg shadow-purple-600/25 transition flex items-center space-x-2">
                            <span>🏛️ TPO Command</span>
                        </button>
                    </div>

                    <!-- Live KPI Highlights -->
                    <div class="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
                        <div class="p-4 bg-white/80 rounded-2xl border border-slate-200/80 shadow-sm text-center">
                            <span class="block text-2xl font-bold font-heading text-slate-900">32+</span>
                            <span class="text-xs text-slate-500 font-medium">Students Profiled</span>
                        </div>
                        <div class="p-4 bg-white/80 rounded-2xl border border-slate-200/80 shadow-sm text-center">
                            <span class="block text-2xl font-bold font-heading text-indigo-600">85–94%</span>
                            <span class="text-xs text-slate-500 font-medium">AI Matching Accuracy</span>
                        </div>
                        <div class="p-4 bg-white/80 rounded-2xl border border-slate-200/80 shadow-sm text-center">
                            <span class="block text-2xl font-bold font-heading text-emerald-600">₹9.0 LPA</span>
                            <span class="text-xs text-slate-500 font-medium">Average Package</span>
                        </div>
                        <div class="p-4 bg-white/80 rounded-2xl border border-slate-200/80 shadow-sm text-center">
                            <span class="block text-2xl font-bold font-heading text-amber-600">0 Conflicts</span>
                            <span class="text-xs text-slate-500 font-medium">Smart Scheduling</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Feature Pillars Section -->
        <section class="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <span class="text-xs uppercase font-bold text-indigo-600 tracking-wider">Comprehensive Architecture</span>
                <h2 class="font-heading font-bold text-3xl text-slate-900 mt-1">Intelligent Placement Lifecycle Automation</h2>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Feature 1 -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div class="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
                        <i data-lucide="gauge" class="w-6 h-6"></i>
                    </div>
                    <h3 class="font-heading font-bold text-lg text-slate-900">Explainable Readiness Scoring</h3>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Evaluates academic records, verified technical breadth, aptitude tests, and mock interview ratings into an explainable 0–100 score with targeted positive factors and improvement areas.
                    </p>
                </div>

                <!-- Feature 2 -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div class="w-12 h-12 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center mb-4">
                        <i data-lucide="cpu" class="w-6 h-6"></i>
                    </div>
                    <h3 class="font-heading font-bold text-lg text-slate-900">Hybrid AI Student-Job Matching</h3>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Combines hard eligibility rules (CGPA, backlogs, branch) with TF-IDF cosine semantic similarity, project relevance, and certifications to rank candidates transparently.
                    </p>
                </div>

                <!-- Feature 3 -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
                        <i data-lucide="calendar" class="w-6 h-6"></i>
                    </div>
                    <h3 class="font-heading font-bold text-lg text-slate-900">Intelligent Conflict-Free Scheduling</h3>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Automatically audits placement drives for student schedule overlaps, venue double-bookings, and panel over-allocations, with an automated sequential rescheduling algorithm.
                    </p>
                </div>

                <!-- Feature 4 -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div class="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
                        <i data-lucide="file-text" class="w-6 h-6"></i>
                    </div>
                    <h3 class="font-heading font-bold text-lg text-slate-900">AI Resume ATS Extraction</h3>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        PDF resume text parsing normalizes industry aliases ("React JS" → React, "ML" → Machine Learning), computes skill gaps, and recommends prioritized preparation milestones.
                    </p>
                </div>

                <!-- Feature 5 -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div class="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4">
                        <i data-lucide="shield-alert" class="w-6 h-6"></i>
                    </div>
                    <h3 class="font-heading font-bold text-lg text-slate-900">Predictive At-Risk Student ML</h3>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Flags students likely to remain unplaced based on aptitude gaps, backlogs, and rejection counts, alerting TPO coordinators to assign mentors before major campus drives.
                    </p>
                </div>

                <!-- Feature 6 -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition">
                    <div class="w-12 h-12 rounded-xl bg-cyan-50 text-cyan-600 flex items-center justify-center mb-4">
                        <i data-lucide="bot" class="w-6 h-6"></i>
                    </div>
                    <h3 class="font-heading font-bold text-lg text-slate-900">Grounded Placement Assistant</h3>
                    <p class="text-xs text-slate-600 mt-2 leading-relaxed">
                        Conversational assistant answering student queries ("Am I eligible for TechNova?", "What skills am I missing for Java Developer?") grounded on real database profiles.
                    </p>
                </div>
            </div>
        </section>
    `;
}

// -------------------------------------------------------------------------------------------------
// 2. STUDENT DASHBOARD
// -------------------------------------------------------------------------------------------------
async function renderStudentDashboard(container, studentId = 1) {
    container.innerHTML = `
        <div class="py-16 text-center">
            <div class="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-xs text-slate-500">Loading student readiness profile & opportunities...</p>
        </div>
    `;

    try {
        const student = await api(`/students/${studentId}`);
        const readinessData = await api(`/students/${studentId}/readiness`);
        const recs = await api(`/students/${studentId}/recommendations`);
        const apps = await api(`/students/${studentId}/applications`);
        const offers = await api(`/students/${studentId}/offers`);
        const docs = await api(`/students/${studentId}/documents`);
        const defaultGaps = await api(`/students/${studentId}/skill-gaps?role_name=Java Backend Developer`);

        let studentInterviews = [];
        try {
            studentInterviews = await api(`/interviews?student_id=${studentId}`);
        } catch (e) {
            studentInterviews = [];
        }

        const skillsList = JSON.parse(student.technical_skills || '[]');
        const certsList = JSON.parse(student.certifications || '[]');
        const projectsList = JSON.parse(student.projects || '[]');

        container.innerHTML = `
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
                <!-- Welcome Banner -->
                <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded bg-indigo-500/30 text-indigo-300 text-[10px] font-bold uppercase tracking-wider border border-indigo-400/30">Candidate Profile</span>
                            <span class="text-slate-400 text-xs">Roll: ${student.student_id}</span>
                        </div>
                        <h2 class="font-heading font-extrabold text-2xl sm:text-3xl mt-1">${student.name}</h2>
                        <p class="text-xs text-slate-300 mt-1">Branch: <b>${student.branch}</b> | CGPA: <b>${student.cgpa}</b> | Active Backlogs: <b>${student.backlogs}</b> | Semester: ${student.semester}</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="openStudentProfileModal(${student.id})" class="px-3.5 py-2 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5">
                            <i data-lucide="edit-3" class="w-4 h-4"></i>
                            <span>Edit Profile</span>
                        </button>
                        <button onclick="document.getElementById('resume-file-input').click()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5">
                            <i data-lucide="upload" class="w-4 h-4"></i>
                            <span>Upload / Audit Resume</span>
                        </button>
                        <input id="resume-file-input" type="file" accept=".pdf,.txt" class="hidden" onchange="handleResumeUpload(event, ${student.id})">
                    </div>
                </div>

                <!-- TOP ROW: READINESS GAUGE + RADAR BREAKDOWN + SKILL GAP -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Card 1: Explainable Readiness Score -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="font-heading font-bold text-base text-slate-900">Placement Readiness</h3>
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${getReadinessBadgeClass(student.readiness_class)}">
                                    ${student.readiness_class}
                                </span>
                            </div>

                            <div class="flex items-center justify-center my-4">
                                <div class="relative w-36 h-36 flex items-center justify-center">
                                    <svg class="w-full h-full gauge-circle" viewBox="0 0 100 100">
                                        <circle cx="50" cy="50" r="40" stroke="#e2e8f0" stroke-width="8" fill="transparent"/>
                                        <circle cx="50" cy="50" r="40" stroke="#4f46e5" stroke-width="8" stroke-dasharray="251.2" stroke-dashoffset="${251.2 - (251.2 * student.readiness_score / 100)}" stroke-linecap="round" fill="transparent"/>
                                    </svg>
                                    <div class="absolute text-center">
                                        <span class="font-heading font-extrabold text-3xl text-slate-900">${student.readiness_score}</span>
                                        <span class="block text-[10px] text-slate-400 uppercase font-semibold">/ 100</span>
                                    </div>
                                </div>
                            </div>

                            <div class="mt-4 space-y-2 text-xs">
                                <p class="font-semibold text-slate-700">Positive Factors:</p>
                                <ul class="space-y-1 text-slate-600">
                                    ${readinessData.positive_factors.map(f => `<li class="flex items-start space-x-1.5"><span class="text-emerald-500 font-bold">✓</span><span>${f}</span></li>`).join('')}
                                </ul>
                            </div>
                        </div>

                        <div class="mt-4 pt-4 border-t border-slate-100 text-xs">
                            <p class="font-semibold text-amber-700">Priority Improvements:</p>
                            <ul class="space-y-1 text-slate-600 mt-1">
                                ${readinessData.improvement_areas.map(a => `<li class="flex items-start space-x-1.5"><span class="text-amber-500 font-bold">•</span><span>${a}</span></li>`).join('')}
                            </ul>
                        </div>
                    </div>

                    <!-- Card 2: 5-Dimensional Competency Radar -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <h3 class="font-heading font-bold text-base text-slate-900">Competency Breakdown</h3>
                                <span class="text-xs text-slate-400">Multi-factor Audit</span>
                            </div>
                            <p class="text-[11px] text-slate-500 mb-4">Weighted performance across assessment & portfolio metrics</p>
                            <div class="h-56 relative flex items-center justify-center">
                                <canvas id="readinessRadarChart"></canvas>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 text-[11px] pt-4 border-t border-slate-100">
                            <div>Aptitude: <b>${student.aptitude_score}%</b></div>
                            <div>Coding: <b>${student.coding_score}%</b></div>
                            <div>Mock Interview: <b>${student.mock_interview_score}%</b></div>
                            <div>Communication: <b>${student.communication_score}%</b></div>
                        </div>
                    </div>

                    <!-- Card 3: Skill Gap Analysis & Recommendations -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <h3 class="font-heading font-bold text-base text-slate-900">Skill Gap Analysis</h3>
                                <select onchange="updateSkillGapComparison(this.value, ${student.id})" class="text-xs px-2 py-1 bg-slate-100 border border-slate-200 rounded-lg focus:outline-none">
                                    <option value="Java Backend Developer">Java Backend</option>
                                    <option value="Full Stack Web Engineer">Full Stack Web</option>
                                    <option value="Cloud & DevOps Engineer">Cloud & DevOps</option>
                                    <option value="AI/ML Associate Engineer">AI/ML Engineer</option>
                                </select>
                            </div>
                            <div id="skill-gap-container" class="space-y-3 text-xs mt-3">
                                <div>
                                    <span class="font-semibold text-slate-700 block mb-1">Available Skills (${defaultGaps.available_skills.length}):</span>
                                    <div class="flex flex-wrap gap-1">
                                        ${defaultGaps.available_skills.map(s => `<span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium">✓ ${s}</span>`).join('')}
                                    </div>
                                </div>

                                <div class="pt-2">
                                    <span class="font-semibold text-slate-700 block mb-1">Missing Requirements (${defaultGaps.missing_skills.length}):</span>
                                    <div class="flex flex-wrap gap-1">
                                        ${defaultGaps.missing_skills.map(s => `<span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-medium">✗ ${s}</span>`).join('')}
                                    </div>
                                </div>

                                <div class="pt-2 border-t border-slate-100">
                                    <span class="font-semibold text-indigo-700 block mb-1">Targeted Prep Plan:</span>
                                    <ul class="space-y-1 text-slate-600">
                                        ${defaultGaps.personalized_recommendations.map(r => `<li class="flex items-start space-x-1.5"><span class="text-indigo-500 font-bold">→</span><span>${r}</span></li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- MIDDLE ROW: RECOMMENDED JOBS ARENA -->
                <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-slate-900">Recommended Opportunities for You</h3>
                            <p class="text-xs text-slate-500">AI-ranked drives based on CGPA, technical skills, projects, and interview ratings</p>
                        </div>
                        <span class="text-xs text-indigo-600 font-semibold">${recs.recommended_jobs.length} Matching Roles</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                        ${recs.recommended_jobs.map(job => `
                            <div class="p-5 rounded-xl border border-slate-200 hover:border-indigo-300 bg-white transition shadow-sm hover:shadow-md flex flex-col justify-between">
                                <div>
                                    <div class="flex items-start justify-between">
                                        <div>
                                            <span class="text-[10px] uppercase font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">${job.company_name}</span>
                                            <h4 class="font-heading font-bold text-base text-slate-900 mt-1">${job.title}</h4>
                                        </div>
                                        <div class="text-right">
                                            <span class="font-heading font-extrabold text-lg text-emerald-600">${job.fit_score}%</span>
                                            <span class="block text-[9px] uppercase font-semibold text-slate-400">Match</span>
                                        </div>
                                    </div>

                                    <div class="mt-3 text-xs text-slate-600 space-y-1">
                                        <p>Package: <b class="text-slate-900">₹${job.ctc_lpa} LPA</b> | Min CGPA: <b>${job.min_cgpa}</b></p>
                                        <p>Location: <b>${job.location}</b></p>
                                    </div>

                                    <div class="mt-3 pt-3 border-t border-slate-100 text-[11px]">
                                        <p class="font-semibold text-slate-700">Matched Skills:</p>
                                        <div class="flex flex-wrap gap-1 mt-1">
                                            ${job.matched_skills.map(s => `<span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px]">✓ ${s}</span>`).join('')}
                                        </div>
                                    </div>
                                </div>

                                <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                                    <button onclick="showExplainModal(${JSON.stringify(job).replace(/"/g, '&quot;')})" class="text-xs text-indigo-600 hover:underline font-medium">Why this score?</button>
                                    <button onclick="applyToJob(${student.id}, ${job.job_id})" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition">
                                        Apply Now
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- APPLICATION PIPELINE & OFFERS -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- My Applications Pipeline -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                        <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                            <h3 class="font-heading font-bold text-base text-slate-900">Application Pipeline Tracker</h3>
                            <span class="text-xs text-slate-500">${apps.length} Active Applications</span>
                        </div>

                        ${apps.length === 0 ? `
                            <p class="text-xs text-slate-500 py-6 text-center">No applications submitted yet. Browse recommended opportunities above.</p>
                        ` : `
                            <div class="space-y-3">
                                ${apps.map(a => `
                                    <div class="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs">
                                        <div>
                                            <span class="font-semibold text-slate-900 block">${a.job_title}</span>
                                            <span class="text-slate-500">${a.company_name} • ₹${a.ctc_lpa} LPA</span>
                                        </div>
                                        <div class="text-right">
                                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${getPipelineBadgeClass(a.status)}">
                                                ${a.status.replace(/_/g, ' ')}
                                            </span>
                                            <span class="block text-[10px] text-slate-400 mt-1">Match: ${a.match_score}%</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `}
                    </div>

                    <!-- Offers & Verified Documents -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                                <h3 class="font-heading font-bold text-base text-slate-900">Placement Offers & Documents</h3>
                                <span class="text-xs font-semibold text-emerald-600">${offers.length} Offer(s)</span>
                            </div>

                            <!-- Offers -->
                            <div class="space-y-3">
                                ${offers.length === 0 ? `
                                    <div class="p-4 rounded-xl border border-dashed border-slate-300 text-center text-xs text-slate-500">
                                        No offers generated yet. Prepare for upcoming mock interviews!
                                    </div>
                                ` : `
                                    ${offers.map(o => `
                                        <div class="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 text-xs">
                                            <div class="flex items-center justify-between">
                                                <div>
                                                    <span class="font-heading font-bold text-slate-900 text-sm block">${o.role_title}</span>
                                                    <span class="text-emerald-800 font-semibold">${o.company_name}</span>
                                                </div>
                                                <div class="text-right">
                                                    <span class="font-heading font-extrabold text-base text-emerald-700">₹${o.ctc_lpa} LPA</span>
                                                    <span class="block text-[10px] uppercase font-bold text-emerald-600">Status: ${o.acceptance_status}</span>
                                                </div>
                                            </div>
                                            <div class="mt-3 pt-2 border-t border-emerald-200/60 flex items-center justify-between text-[11px] text-slate-600">
                                                <span>Joining: <b>${o.joining_date || 'TBD'}</b> (${o.joining_status})</span>
                                                <span>Docs: <b>${o.documentation_status}</b></span>
                                            </div>
                                            ${o.acceptance_status === 'PENDING' ? `
                                                <div class="mt-3 pt-2 border-t border-emerald-200/60 flex items-center justify-end space-x-2">
                                                    <button onclick="respondToOffer(${student.id}, ${o.id}, 'ACCEPT')" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold text-xs transition shadow-sm">
                                                        Accept Offer
                                                    </button>
                                                    <button onclick="respondToOffer(${student.id}, ${o.id}, 'REJECT')" class="px-3 py-1 bg-slate-200 hover:bg-rose-100 hover:text-rose-700 text-slate-700 rounded-lg font-medium text-xs transition">
                                                        Decline
                                                    </button>
                                                </div>
                                            ` : ''}
                                        </div>
                                    `).join('')}
                                `}
                            </div>
                        </div>

                        <!-- Documents Status -->
                        <div class="mt-6 pt-4 border-t border-slate-100 text-xs">
                            <span class="font-semibold text-slate-700 block mb-2">Verified Documents (${docs.length}):</span>
                            <div class="flex flex-wrap gap-2">
                                ${docs.map(d => `
                                    <span class="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-[11px] flex items-center space-x-1 border border-slate-200">
                                        <span>📄</span>
                                        <span>${d.title}</span>
                                        <span class="text-emerald-600 font-bold ml-1">✓</span>
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- INTERVIEW ROUNDS TRACKER -->
                <div class="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                    <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                        <div>
                            <h3 class="font-heading font-bold text-base text-slate-900">Upcoming & Evaluated Interview Rounds</h3>
                            <p class="text-xs text-slate-500">Live interview status, panel schedules, ratings, and feedback</p>
                        </div>
                        <span class="text-xs font-semibold text-indigo-600">${studentInterviews.length} Round(s)</span>
                    </div>

                    ${studentInterviews.length === 0 ? `
                        <div class="p-6 rounded-xl border border-dashed border-slate-200 text-center text-xs text-slate-500">
                            No interview rounds scheduled yet. When shortlisted by recruiters or TPO, interview schedules will appear here.
                        </div>
                    ` : `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            ${studentInterviews.map(it => `
                                <div class="p-4 rounded-xl border ${it.status === 'COMPLETED' ? 'border-emerald-200 bg-emerald-50/30' : 'border-indigo-200 bg-indigo-50/30'} flex flex-col justify-between text-xs">
                                    <div>
                                        <div class="flex items-start justify-between">
                                            <div>
                                                <span class="text-[10px] font-bold uppercase text-indigo-700 bg-indigo-100/60 px-2 py-0.5 rounded">${it.company_name}</span>
                                                <h4 class="font-heading font-bold text-sm text-slate-900 mt-1">${it.round_name}</h4>
                                                <span class="text-slate-500 text-[11px]">${it.job_title}</span>
                                            </div>
                                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${it.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-100 text-indigo-800'}">
                                                ${it.status}
                                            </span>
                                        </div>

                                        <div class="mt-3 pt-2 border-t border-slate-200/60 space-y-1 text-slate-600 text-[11px]">
                                            <p>Scheduled: <b class="text-slate-800">${it.scheduled_time}</b></p>
                                            <p>Panel: <b class="text-slate-800">${it.interviewer_panel}</b></p>
                                        </div>

                                        ${it.status === 'COMPLETED' ? `
                                            <div class="mt-3 pt-2 border-t border-slate-200/60 space-y-1">
                                                <div class="flex items-center space-x-3 text-[11px]">
                                                    <span>Tech: <b class="text-emerald-700">${it.technical_rating}/10</b></span>
                                                    <span>Comm: <b class="text-indigo-700">${it.comm_rating}/10</b></span>
                                                    <span>Decision: <b class="${it.recommendation === 'SELECT' ? 'text-emerald-700 font-bold' : (it.recommendation === 'REJECT' ? 'text-rose-700 font-bold' : 'text-amber-700 font-bold')}">${it.recommendation}</b></span>
                                                </div>
                                                ${it.feedback ? `<p class="text-slate-600 italic text-[11px] mt-1 bg-white/80 p-2 rounded border border-slate-200">"${it.feedback}"</p>` : ''}
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>
            </div>
        `;

        lucide.createIcons();
        initReadinessRadar(readinessData.dimensions);
    } catch (err) {
        container.innerHTML = `<div class="p-8 text-center text-rose-600 text-sm">Failed to load student dashboard: ${err.message}</div>`;
    }
}

function initReadinessRadar(dimensions) {
    const ctx = document.getElementById('readinessRadarChart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Academic', 'Technical', 'Aptitude', 'Interview', 'Projects'],
            datasets: [{
                label: 'Candidate Score',
                data: [
                    dimensions.academic || 75,
                    dimensions.technical || 80,
                    dimensions.aptitude || 70,
                    dimensions.interview || 75,
                    dimensions.projects || 70
                ],
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: '#e2e8f0' },
                    grid: { color: '#f1f5f9' },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

async function updateSkillGapComparison(roleName, studentId) {
    const container = document.getElementById('skill-gap-container');
    container.innerHTML = `<div class="py-4 text-center text-slate-400 text-xs">Analyzing skill gaps for ${roleName}...</div>`;
    try {
        const gap = await api(`/students/${studentId}/skill-gaps?role_name=${encodeURIComponent(roleName)}`);
        container.innerHTML = `
            <div>
                <span class="font-semibold text-slate-700 block mb-1">Available Skills (${gap.available_skills.length}):</span>
                <div class="flex flex-wrap gap-1">
                    ${gap.available_skills.map(s => `<span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium">✓ ${s}</span>`).join('')}
                </div>
            </div>

            <div class="pt-2">
                <span class="font-semibold text-slate-700 block mb-1">Missing Requirements (${gap.missing_skills.length}):</span>
                <div class="flex flex-wrap gap-1">
                    ${gap.missing_skills.map(s => `<span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-medium">✗ ${s}</span>`).join('')}
                </div>
            </div>

            <div class="pt-2 border-t border-slate-100">
                <span class="font-semibold text-indigo-700 block mb-1">Targeted Prep Plan:</span>
                <ul class="space-y-1 text-slate-600">
                    ${gap.personalized_recommendations.map(r => `<li class="flex items-start space-x-1.5"><span class="text-indigo-500 font-bold">→</span><span>${r}</span></li>`).join('')}
                </ul>
            </div>
        `;
    } catch (e) {
        showToast("Error updating skill gaps: " + e.message, 'error');
    }
}

async function handleResumeUpload(event, studentId) {
    const file = event.target.files[0];
    if (!file) return;

    showToast(`Parsing resume "${file.name}" with AI NLP...`, 'info');
    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await api(`/students/${studentId}/resume`, {
            method: 'POST',
            body: formData
        });
        showToast(`Resume audited! Extracted ${res.nlp_results.detected_skills.length} skills. Readiness: ${res.readiness_score}/100`, 'success');
        renderStudentDashboard(document.getElementById('app-content'), studentId);
    } catch (err) {
        showToast("Resume parsing failed: " + err.message, 'error');
    }
}

async function applyToJob(studentId, jobId) {
    try {
        const res = await api(`/students/${studentId}/apply`, {
            method: 'POST',
            body: JSON.stringify({ job_id: jobId })
        });
        showToast(res.message, 'success');
        renderStudentDashboard(document.getElementById('app-content'), studentId);
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 3. RECRUITER DASHBOARD
// -------------------------------------------------------------------------------------------------
async function renderRecruiterDashboard(container) {
    container.innerHTML = `
        <div class="py-16 text-center">
            <div class="w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-xs text-slate-500">Loading recruiter candidate ranking arena...</p>
        </div>
    `;

    try {
        const jobs = await api('/jobs');
        state.cachedJobs = jobs;
        const activeJobId = state.selectedJobForMatching || (jobs[0] ? jobs[0].id : 1);
        const candidatesData = await api(`/jobs/${activeJobId}/candidates`);

        let activeInterviews = [];
        try {
            activeInterviews = await api('/interviews');
        } catch (e) {
            activeInterviews = [];
        }

        container.innerHTML = `
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
                <!-- Recruiter Header -->
                <div class="bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded bg-teal-500/30 text-teal-300 text-[10px] font-bold uppercase tracking-wider border border-teal-400/30">Corporate Recruiter Portal</span>
                        </div>
                        <h2 class="font-heading font-extrabold text-2xl sm:text-3xl mt-1">TechNova Solutions — Talent Acquisition</h2>
                        <p class="text-xs text-slate-300 mt-1">Post roles with AI NLP parser, evaluate ranked candidate matches, and shortlist applicants.</p>
                    </div>
                    <button onclick="openJobCreateModal()" class="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5">
                        <i data-lucide="plus" class="w-4 h-4"></i>
                        <span>Post New Job (AI NLP)</span>
                    </button>
                </div>

                <!-- SELECT ACTIVE ROLE BAR -->
                <div class="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div class="flex items-center space-x-3 w-full sm:w-auto">
                        <label class="text-xs font-semibold text-slate-700 whitespace-nowrap">Active Job Role:</label>
                        <select onchange="changeRecruiterRole(this.value)" class="text-xs px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 w-full sm:w-72 font-medium">
                            ${jobs.map(j => `<option value="${j.id}" ${j.id === activeJobId ? 'selected' : ''}>${j.title} (₹${j.ctc_lpa} LPA)</option>`).join('')}
                        </select>
                    </div>

                    <!-- Filter pills -->
                    <div class="flex items-center flex-wrap gap-2 text-xs">
                        <input id="candidate-skill-filter" type="text" placeholder="Filter by skill (e.g. Java)..." class="px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg" onkeyup="filterCandidatesTable()">
                        <select id="candidate-branch-filter" class="px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg" onchange="filterCandidatesTable()">
                            <option value="ALL">All Branches</option>
                            <option value="CSE">CSE</option>
                            <option value="IT">IT</option>
                            <option value="ECE">ECE</option>
                            <option value="EEE">EEE</option>
                            <option value="ME">ME</option>
                            <option value="Civil">Civil</option>
                        </select>
                    </div>
                </div>

                <!-- CANDIDATE RANKING TABLE -->
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
                    <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-slate-900">Ranked Candidate Matches for ${candidatesData.job_title}</h3>
                            <p class="text-xs text-slate-500">Sorted by Hybrid AI Fit Score (eligibility rules, TF-IDF skill cosine similarity, projects & assessments)</p>
                        </div>
                        <button onclick="shortlistSelectedCandidates(${activeJobId})" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold transition flex items-center space-x-1.5">
                            <i data-lucide="check-check" class="w-4 h-4"></i>
                            <span>Shortlist Selected</span>
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-600 font-semibold uppercase text-[10px] tracking-wider border-b border-slate-200">
                                <tr>
                                    <th class="p-4 w-10 text-center"><input type="checkbox" id="select-all-cands" onchange="toggleSelectAllCandidates(this)"></th>
                                    <th class="p-4">Rank & Candidate</th>
                                    <th class="p-4">Branch & CGPA</th>
                                    <th class="p-4">Readiness</th>
                                    <th class="p-4">AI Fit Score</th>
                                    <th class="p-4">Application Status</th>
                                    <th class="p-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="candidates-table-body" class="divide-y divide-slate-100">
                                ${candidatesData.candidates.map((c, index) => `
                                    <tr class="hover:bg-slate-50/80 transition cand-row" data-branch="${c.branch}" data-skills="${(c.matched_skills || []).join(' ').toLowerCase()}">
                                        <td class="p-4 text-center">
                                            <input type="checkbox" class="cand-checkbox" value="${c.student_id}">
                                        </td>
                                        <td class="p-4">
                                            <div class="flex items-center space-x-2.5">
                                                <span class="w-6 h-6 rounded-full bg-slate-100 text-slate-600 font-bold flex items-center justify-center text-[10px]">${index + 1}</span>
                                                <div>
                                                    <span class="font-semibold text-slate-900 block">${c.name}</span>
                                                    <span class="text-slate-400 text-[10px]">${c.student_roll} • ${c.email}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="p-4">
                                            <span class="font-medium text-slate-800">${c.branch}</span>
                                            <span class="block text-slate-500 text-[11px]">CGPA: ${c.cgpa} ${c.backlogs > 0 ? `<span class="text-rose-600 font-bold">(${c.backlogs} bl)</span>` : ''}</span>
                                        </td>
                                        <td class="p-4">
                                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${getReadinessBadgeClass(c.readiness_class)}">
                                                ${c.readiness_score}/100
                                            </span>
                                        </td>
                                        <td class="p-4">
                                            <div class="flex items-center space-x-2">
                                                <span class="font-heading font-extrabold text-sm ${c.fit_score >= 80 ? 'text-emerald-600' : (c.fit_score >= 65 ? 'text-indigo-600' : 'text-amber-600')}">
                                                    ${c.fit_score}%
                                                </span>
                                                <div class="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                                    <div class="bg-indigo-600 h-full rounded-full" style="width: ${c.fit_score}%"></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="p-4">
                                            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${getPipelineBadgeClass(c.application_status)}">
                                                ${c.application_status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td class="p-4 text-right space-x-1.5 whitespace-nowrap">
                                            <button onclick="showCandidateExplainModal(${JSON.stringify(c).replace(/"/g, '&quot;')}, '${candidatesData.job_title}')" class="px-2.5 py-1 rounded bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-semibold transition">
                                                Explain Match
                                            </button>
                                            <button onclick="openScheduleInterviewModal(${c.application_id || 'null'}, ${c.student_id}, '${c.name.replace(/'/g, "\\'")}', '${candidatesData.job_title.replace(/'/g, "\\'")}')" class="px-2.5 py-1 rounded bg-teal-50 hover:bg-teal-100 text-teal-700 text-xs font-semibold transition">
                                                Schedule Round
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- INTERVIEWS & EVALUATION TRACKER TABLE -->
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
                    <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-slate-900">Interview Schedules & Evaluations Arena</h3>
                            <p class="text-xs text-slate-500">Track candidate interview panels, record technical & communication scores, and submit final recommendations</p>
                        </div>
                        <span class="text-xs font-semibold text-teal-700">${activeInterviews.length} Scheduled / Completed Rounds</span>
                    </div>

                    ${activeInterviews.length === 0 ? `
                        <p class="p-6 text-center text-xs text-slate-500">No interview rounds currently logged. Click "Schedule Round" on any candidate above.</p>
                    ` : `
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead class="bg-slate-50 text-slate-600 font-semibold uppercase text-[10px] tracking-wider border-b border-slate-200">
                                    <tr>
                                        <th class="p-4">Candidate & Role</th>
                                        <th class="p-4">Round</th>
                                        <th class="p-4">Schedule Time</th>
                                        <th class="p-4">Panel Assigned</th>
                                        <th class="p-4">Status</th>
                                        <th class="p-4">Ratings (Tech / Comm)</th>
                                        <th class="p-4">Recommendation</th>
                                        <th class="p-4 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    ${activeInterviews.map(it => `
                                        <tr class="hover:bg-slate-50 transition">
                                            <td class="p-4">
                                                <span class="font-semibold text-slate-900 block">${it.student_name}</span>
                                                <span class="text-slate-400 text-[10px]">${it.job_title}</span>
                                            </td>
                                            <td class="p-4 font-medium text-slate-800">${it.round_name}</td>
                                            <td class="p-4 text-indigo-700 font-medium">${it.scheduled_time}</td>
                                            <td class="p-4 text-slate-600">${it.interviewer_panel}</td>
                                            <td class="p-4">
                                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${it.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-100 text-indigo-800'}">
                                                    ${it.status}
                                                </span>
                                            </td>
                                            <td class="p-4 font-semibold text-slate-700">
                                                ${it.status === 'COMPLETED' ? `${it.technical_rating} / ${it.comm_rating}` : 'Pending Evaluation'}
                                            </td>
                                            <td class="p-4">
                                                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${it.recommendation === 'SELECT' ? 'bg-emerald-100 text-emerald-800' : (it.recommendation === 'REJECT' ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700')}">
                                                    ${it.recommendation}
                                                </span>
                                            </td>
                                            <td class="p-4 text-right">
                                                <button onclick="openInterviewFeedbackModal(${it.id}, '${(it.student_name || '').replace(/'/g, "\\'")}', '${(it.round_name || '').replace(/'/g, "\\'")}', ${it.technical_rating || 8.0}, ${it.comm_rating || 7.5}, '${it.recommendation || 'PROGRESS'}', '${(it.feedback || '').replace(/'/g, "\\'")}')" class="px-2.5 py-1 rounded bg-teal-50 hover:bg-teal-100 text-teal-700 font-semibold text-xs transition">
                                                    Evaluate
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            </div>
        `;

        lucide.createIcons();
    } catch (err) {
        container.innerHTML = `<div class="p-8 text-center text-rose-600 text-sm">Failed to load recruiter arena: ${err.message}</div>`;
    }
}

function changeRecruiterRole(jobId) {
    state.selectedJobForMatching = parseInt(jobId);
    renderRecruiterDashboard(document.getElementById('app-content'));
}

function toggleSelectAllCandidates(master) {
    const boxes = document.querySelectorAll('.cand-checkbox');
    boxes.forEach(b => b.checked = master.checked);
}

async function shortlistSelectedCandidates(jobId) {
    const checked = Array.from(document.querySelectorAll('.cand-checkbox:checked')).map(cb => parseInt(cb.value));
    if (checked.length === 0) {
        showToast("Please select at least one candidate using the checkboxes.", 'warning');
        return;
    }
    showToast(`Shortlisting ${checked.length} candidates and sending notifications...`, 'info');
    try {
        const res = await api(`/jobs/${jobId}/shortlist`, {
            method: 'POST',
            body: JSON.stringify({ student_ids: checked })
        });
        showToast(res.message, 'success');
        renderRecruiterDashboard(document.getElementById('app-content'));
    } catch (e) {
        showToast("Shortlisting failed: " + e.message, 'error');
    }
}

function filterCandidatesTable() {
    const branch = document.getElementById('candidate-branch-filter').value;
    const skill = (document.getElementById('candidate-skill-filter').value || '').toLowerCase().trim();
    const rows = document.querySelectorAll('.cand-row');

    rows.forEach(r => {
        const rBranch = r.getAttribute('data-branch');
        const rSkills = r.getAttribute('data-skills');
        const branchMatch = (branch === 'ALL' || rBranch === branch);
        const skillMatch = (!skill || rSkills.includes(skill));
        r.style.display = (branchMatch && skillMatch) ? '' : 'none';
    });
}

// -------------------------------------------------------------------------------------------------
// 4. ADMIN DASHBOARD & COMMAND CENTER
// -------------------------------------------------------------------------------------------------
async function renderAdminDashboard(container) {
    container.innerHTML = `
        <div class="py-16 text-center">
            <div class="w-10 h-10 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-xs text-slate-500">Loading TPO placement command center & live analytics...</p>
        </div>
    `;

    try {
        const kpis = await api('/analytics/dashboard');
        const conflictReport = await api('/scheduling/conflicts');

        container.innerHTML = `
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
                <!-- TPO Command Header -->
                <div class="bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded bg-purple-500/30 text-purple-300 text-[10px] font-bold uppercase tracking-wider border border-purple-400/30">TPO Central Command</span>
                            <span class="text-slate-400 text-xs">Academic Session 2026</span>
                        </div>
                        <h2 class="font-heading font-extrabold text-2xl sm:text-3xl mt-1">Placement Cell Administration & Analytics</h2>
                        <p class="text-xs text-slate-300 mt-1">Comprehensive audit of readiness profiles, drive conflicts, offer disbursements, and predictive at-risk interventions.</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="triggerQuickConflictDemo()" class="px-4 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5">
                            <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                            <span>Audit Conflicts (${conflictReport.total_conflicts})</span>
                        </button>
                    </div>
                </div>

                <!-- CONFLICT BANNER IF CONFLICTS EXIST -->
                ${conflictReport.has_conflicts ? `
                    <div class="p-5 rounded-2xl bg-amber-50 border border-amber-300 shadow-sm text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 conflict-pulse">
                        <div class="flex items-start space-x-3">
                            <div class="p-2 rounded-lg bg-amber-200 text-amber-900 font-bold">
                                ⚠
                            </div>
                            <div>
                                <h4 class="font-heading font-bold text-sm text-amber-900">${conflictReport.total_conflicts} Schedule Conflict(s) Detected in Active Drives!</h4>
                                <p class="text-amber-800 mt-0.5">Venue double-booking, panel over-allocations, or candidate interview clashes detected.</p>
                            </div>
                        </div>
                        <button onclick="switchAdminTab('drives')" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-xl text-xs transition shadow-sm whitespace-nowrap">
                            Review & Auto-Optimize
                        </button>
                    </div>
                ` : ''}

                <!-- COMMAND TABS NAVIGATION -->
                <div class="border-b border-slate-200 flex items-center space-x-1 overflow-x-auto text-xs font-semibold">
                    <button onclick="switchAdminTab('overview')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'overview' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition">
                        Overview & KPIs
                    </button>
                    <button onclick="switchAdminTab('analytics')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'analytics' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition">
                        Interactive Analytics
                    </button>
                    <button onclick="switchAdminTab('drives')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'drives' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition flex items-center space-x-1">
                        <span>Drive Scheduling & Conflicts</span>
                        ${conflictReport.has_conflicts ? `<span class="px-1.5 py-0.2 bg-amber-500 text-white rounded-full text-[9px]">${conflictReport.total_conflicts}</span>` : ''}
                    </button>
                    <button onclick="switchAdminTab('pipeline')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'pipeline' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition">
                        Application Pipeline
                    </button>
                    <button onclick="switchAdminTab('offers')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'offers' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition">
                        Offers & Joining
                    </button>
                    <button onclick="switchAdminTab('documents')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'documents' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition">
                        Document Verification
                    </button>
                    <button onclick="switchAdminTab('atrisk')" class="admin-tab-btn px-4 py-3 border-b-2 ${state.adminTab === 'atrisk' ? 'border-indigo-600 text-indigo-600 font-bold' : 'border-transparent text-slate-500 hover:text-slate-800'} transition flex items-center space-x-1">
                        <span>Predictive At-Risk Model</span>
                        <span class="px-1.5 py-0.2 bg-rose-500 text-white rounded-full text-[9px]">${kpis.students_at_risk}</span>
                    </button>
                </div>

                <!-- TAB CONTENT CONTAINER -->
                <div id="admin-tab-content">
                    <!-- Populated dynamically -->
                </div>
            </div>
        `;

        lucide.createIcons();
        renderAdminTabContent(kpis, conflictReport);
    } catch (err) {
        container.innerHTML = `<div class="p-8 text-center text-rose-600 text-sm">Failed to load admin command center: ${err.message}</div>`;
    }
}

function switchAdminTab(tabName) {
    state.adminTab = tabName;
    renderAdminDashboard(document.getElementById('app-content'));
}

async function renderAdminTabContent(kpis, conflictReport) {
    const container = document.getElementById('admin-tab-content');
    if (!container) return;

    if (state.adminTab === 'overview') {
        // TAB 1: OVERVIEW & 10 KPI CARDS + RECENT ROSTER
        container.innerHTML = `
            <div class="space-y-8">
                <!-- 10 KPI CARDS GRID -->
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Total Registered</span>
                        <span class="block font-heading font-extrabold text-2xl text-slate-900 mt-1">${kpis.total_students}</span>
                        <span class="text-[10px] text-slate-400">All Batches</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Placement Ready</span>
                        <span class="block font-heading font-extrabold text-2xl text-indigo-600 mt-1">${kpis.placement_ready_students}</span>
                        <span class="text-[10px] text-indigo-500 font-semibold">${Math.round(kpis.placement_ready_students/kpis.total_students*100)}% of Cohort</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Students Placed</span>
                        <span class="block font-heading font-extrabold text-2xl text-emerald-600 mt-1">${kpis.students_placed}</span>
                        <span class="text-[10px] text-emerald-600 font-semibold">${kpis.placement_percentage}% Placed</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Total Recruiters</span>
                        <span class="block font-heading font-extrabold text-2xl text-teal-600 mt-1">${kpis.total_recruiters}</span>
                        <span class="text-[10px] text-teal-500">Corporate Partners</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Active Drives</span>
                        <span class="block font-heading font-extrabold text-2xl text-slate-900 mt-1">${kpis.active_drives}</span>
                        <span class="text-[10px] text-slate-400">This Month</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Offers Generated</span>
                        <span class="block font-heading font-extrabold text-2xl text-purple-600 mt-1">${kpis.offers_made}</span>
                        <span class="text-[10px] text-purple-500">${kpis.offers_accepted} Accepted</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Average Package</span>
                        <span class="block font-heading font-extrabold text-2xl text-emerald-600 mt-1">₹${kpis.average_package_lpa} LPA</span>
                        <span class="text-[10px] text-emerald-500">Competitive Mean</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Highest Package</span>
                        <span class="block font-heading font-extrabold text-2xl text-emerald-700 mt-1">₹${kpis.highest_package_lpa} LPA</span>
                        <span class="text-[10px] text-slate-400">Top Tier</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Students At Risk</span>
                        <span class="block font-heading font-extrabold text-2xl text-rose-600 mt-1">${kpis.students_at_risk}</span>
                        <span class="text-[10px] text-rose-500 font-semibold">Intervention Required</span>
                    </div>
                    <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
                        <span class="text-xs text-slate-500 font-medium">Unplaced Pool</span>
                        <span class="block font-heading font-extrabold text-2xl text-slate-700 mt-1">${kpis.students_unplaced}</span>
                        <span class="text-[10px] text-slate-400">Active Candidates</span>
                    </div>
                </div>

                <!-- STUDENT ROSTER SUMMARY TABLE -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
                        <div>
                            <h3 class="font-heading font-bold text-lg text-slate-900">Student Placement Profiles Roster</h3>
                            <p class="text-xs text-slate-500">Live profiles audited for readiness, backlogs, and target drive eligibility</p>
                        </div>
                    </div>
                    <div class="overflow-x-auto mt-4">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-600 uppercase text-[10px] font-semibold border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Candidate</th>
                                    <th class="p-3">Branch</th>
                                    <th class="p-3">CGPA</th>
                                    <th class="p-3">Backlogs</th>
                                    <th class="p-3">Readiness Score</th>
                                    <th class="p-3">Risk Level</th>
                                    <th class="p-3 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="roster-table-body" class="divide-y divide-slate-100">
                                <tr><td colspan="7" class="p-4 text-center text-slate-400">Loading student roster...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        loadStudentRoster();

    } else if (state.adminTab === 'analytics') {
        // TAB 2: INTERACTIVE ANALYTICS (BRANCH, SKILL, PACKAGE, PIPELINE, RECRUITER)
        container.innerHTML = `
            <div class="space-y-8">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Chart 1: Branch-wise Placement Rate -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
                        <h4 class="font-heading font-bold text-base text-slate-900 mb-1">Branch-wise Placement % & CTC</h4>
                        <p class="text-xs text-slate-500 mb-4">Placement conversion across engineering branches</p>
                        <div class="h-64 relative">
                            <canvas id="branchPlacementChart"></canvas>
                        </div>
                    </div>

                    <!-- Chart 2: Package Bracket Distribution -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
                        <h4 class="font-heading font-bold text-base text-slate-900 mb-1">Package Distribution (LPA)</h4>
                        <p class="text-xs text-slate-500 mb-4">CTC breakdown across campus recruitment offers</p>
                        <div class="h-64 relative flex items-center justify-center">
                            <canvas id="packageDistChart"></canvas>
                        </div>
                    </div>

                    <!-- Chart 3: Skill Demand vs Placement -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
                        <h4 class="font-heading font-bold text-base text-slate-900 mb-1">Top In-Demand Skills vs Placement</h4>
                        <p class="text-xs text-slate-500 mb-4">Correlation of candidate technical skills with successful offers</p>
                        <div class="h-64 relative">
                            <canvas id="skillPlacementChart"></canvas>
                        </div>
                    </div>

                    <!-- Chart 4: Placement Funnel Trend -->
                    <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
                        <h4 class="font-heading font-bold text-base text-slate-900 mb-1">Application Pipeline Funnel</h4>
                        <p class="text-xs text-slate-500 mb-4">Conversion volume from application to joined</p>
                        <div class="h-64 relative">
                            <canvas id="pipelineFunnelChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Recruiter Analytics Table -->
                <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
                    <h4 class="font-heading font-bold text-base text-slate-900 mb-1">Corporate Partner Performance</h4>
                    <p class="text-xs text-slate-500 mb-4">Recruiter visits, offers disbursed, and average packages</p>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-600 font-semibold uppercase text-[10px] border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Company</th>
                                    <th class="p-3">Industry</th>
                                    <th class="p-3">Roles Posted</th>
                                    <th class="p-3">Offers Made</th>
                                    <th class="p-3">Average Package</th>
                                    <th class="p-3">Engagement</th>
                                </tr>
                            </thead>
                            <tbody id="recruiter-analytics-body" class="divide-y divide-slate-100">
                                <tr><td colspan="6" class="p-4 text-center text-slate-400">Loading recruiter analytics...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        initAnalyticsCharts();

    } else if (state.adminTab === 'drives') {
        // TAB 3: PLACEMENT DRIVES & SCHEDULING CONFLICT DETECTOR
        const drives = await api('/scheduling/drives');
        container.innerHTML = `
            <div class="space-y-6">
                <!-- CONFLICT DETECTION ACTION BOX -->
                <div class="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold uppercase">AI Conflict Engine</span>
                            <span class="text-xs text-slate-500">Venue, Panel & Student Overlap Analysis</span>
                        </div>
                        <h3 class="font-heading font-bold text-xl text-slate-900 mt-1">Smart Drive Scheduling & Conflict Detector</h3>
                        <p class="text-xs text-slate-600 mt-1">Detects double-booked venues, simultaneous interview panel assignments, and multi-drive candidate overlaps.</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="openCreateDriveModal()" class="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5">
                            <i data-lucide="calendar-plus" class="w-4 h-4"></i>
                            <span>+ Schedule New Drive</span>
                        </button>
                        <button onclick="runAutoScheduleOptimization()" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5">
                            <i data-lucide="sparkles" class="w-4 h-4"></i>
                            <span>Run Schedule Optimizer</span>
                        </button>
                    </div>
                </div>

                <!-- CONFLICT REPORT SUMMARY IF PRESENT -->
                ${conflictReport.has_conflicts ? `
                    <div class="bg-rose-50 border border-rose-200 rounded-2xl p-6 space-y-4">
                        <div class="flex items-center space-x-2 text-rose-800 font-heading font-bold text-sm">
                            <i data-lucide="alert-octagon" class="w-5 h-5 text-rose-600"></i>
                            <span>${conflictReport.total_conflicts} Critical Scheduling Conflicts Detected:</span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                            ${conflictReport.venue_conflicts.map(v => `
                                <div class="p-3.5 bg-white rounded-xl border border-rose-200 shadow-sm">
                                    <span class="font-bold text-rose-700 block">⚠ Venue Double-Booking</span>
                                    <p class="text-slate-700 mt-1">${v.message}</p>
                                </div>
                            `).join('')}
                            ${conflictReport.panel_conflicts.map(p => `
                                <div class="p-3.5 bg-white rounded-xl border border-rose-200 shadow-sm">
                                    <span class="font-bold text-rose-700 block">⚠ Panel Over-Allocation</span>
                                    <p class="text-slate-700 mt-1">${p.message}</p>
                                </div>
                            `).join('')}
                            ${conflictReport.student_conflicts.map(s => `
                                <div class="p-3.5 bg-white rounded-xl border border-rose-200 shadow-sm">
                                    <span class="font-bold text-rose-700 block">⚠ Candidate Schedule Clash</span>
                                    <p class="text-slate-700 mt-1">${s.message}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <div class="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center space-x-2">
                        <span>✓</span>
                        <span class="font-semibold">All active placement drives are completely conflict-free. No venue or candidate clashes.</span>
                    </div>
                `}

                <!-- ACTIVE DRIVES TABLE -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <h4 class="font-heading font-bold text-base text-slate-900 mb-4">Active Campus Placement Drives</h4>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50 text-slate-600 font-semibold uppercase text-[10px] border-b border-slate-200">
                                <tr>
                                    <th class="p-3">Drive / Company</th>
                                    <th class="p-3">Role</th>
                                    <th class="p-3">Date</th>
                                    <th class="p-3">Window</th>
                                    <th class="p-3">Venue</th>
                                    <th class="p-3">Panel Assigned</th>
                                    <th class="p-3">Status</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${drives.map(d => `
                                    <tr class="hover:bg-slate-50 transition">
                                        <td class="p-3 font-semibold text-slate-900">${d.company_name}</td>
                                        <td class="p-3 text-slate-700">${d.role_title}</td>
                                        <td class="p-3 text-slate-600">${d.drive_date}</td>
                                        <td class="p-3 font-medium text-indigo-700">${d.start_time} - ${d.end_time}</td>
                                        <td class="p-3"><span class="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 font-medium">${d.venue}</span></td>
                                        <td class="p-3 text-slate-600">${d.panel_name}</td>
                                        <td class="p-3"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700">${d.status}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

    } else if (state.adminTab === 'pipeline') {
        // TAB 4: APPLICATION PIPELINE MANAGER
        const apps = await api('/admin/applications');
        container.innerHTML = `
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                    <div>
                        <h3 class="font-heading font-bold text-lg text-slate-900">Application Pipeline Controller</h3>
                        <p class="text-xs text-slate-500">Transition candidates through Shortlisted, Assessment, Interview, Selected, and Offer stages</p>
                    </div>
                    <span class="text-xs text-indigo-600 font-semibold">${apps.length} Total Applications</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 text-slate-600 uppercase text-[10px] font-semibold border-b border-slate-200">
                            <tr>
                                <th class="p-3">Candidate</th>
                                <th class="p-3">Role & Company</th>
                                <th class="p-3">Match Score</th>
                                <th class="p-3">Current Pipeline Status</th>
                                <th class="p-3 text-right">Pipeline Action</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            ${apps.map(a => `
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-3">
                                        <span class="font-semibold text-slate-900 block">${a.student_name}</span>
                                        <span class="text-slate-400 text-[10px]">${a.branch} • CGPA: ${a.cgpa}</span>
                                    </td>
                                    <td class="p-3">
                                        <span class="font-medium text-slate-800">${a.job_title}</span>
                                        <span class="text-slate-500 block text-[10px]">${a.company_name}</span>
                                    </td>
                                    <td class="p-3 font-heading font-bold text-indigo-600">${a.match_score}%</td>
                                    <td class="p-3">
                                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${getPipelineBadgeClass(a.status)}">
                                            ${a.status.replace(/_/g, ' ')}
                                        </span>
                                    </td>
                                    <td class="p-3 text-right space-x-1 whitespace-nowrap">
                                        <select onchange="updateAppPipelineStage(${a.id}, this.value)" class="text-[11px] px-2 py-1 bg-slate-50 border border-slate-200 rounded-lg">
                                            <option value="">Move to...</option>
                                            <option value="AI_SHORTLISTED">AI Shortlisted</option>
                                            <option value="ASSESSMENT">Assessment</option>
                                            <option value="INTERVIEW">Interview</option>
                                            <option value="SELECTED">Selected</option>
                                            <option value="OFFER_GENERATED">Offer Generated</option>
                                            <option value="REJECTED">Rejected</option>
                                        </select>
                                        <button onclick="openScheduleInterviewModal(${a.id}, ${a.student_id}, '${a.student_name.replace(/'/g, "\\'")}', '${a.job_title.replace(/'/g, "\\'")}')" class="px-2 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded text-[11px] font-semibold" title="Schedule Interview Round">
                                            Interview
                                        </button>
                                        <button onclick="openCreateOfferModal(${a.id}, ${a.student_id}, '${a.student_name.replace(/'/g, "\\'")}', '${a.company_name.replace(/'/g, "\\'")}', '${a.job_title.replace(/'/g, "\\'")}')" class="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded text-[11px] font-semibold" title="Issue Placement Offer">
                                            Offer
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

    } else if (state.adminTab === 'offers') {
        // TAB 5: OFFERS & JOINING CONSOLE
        const offers = await api('/admin/offers');
        container.innerHTML = `
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                    <div>
                        <h3 class="font-heading font-bold text-lg text-slate-900">Placement Offers & Joining Registry</h3>
                        <p class="text-xs text-slate-500">Track offer acceptance, joining verification, and official letters</p>
                    </div>
                    <button onclick="openCreateOfferModal()" class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-1.5 self-start sm:self-auto">
                        <i data-lucide="award" class="w-4 h-4"></i>
                        <span>+ Issue New Offer</span>
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 text-slate-600 uppercase text-[10px] font-semibold border-b border-slate-200">
                            <tr>
                                <th class="p-3">Candidate ID</th>
                                <th class="p-3">Company & Role</th>
                                <th class="p-3">CTC</th>
                                <th class="p-3">Offer Date</th>
                                <th class="p-3">Acceptance</th>
                                <th class="p-3">Joining Status</th>
                                <th class="p-3">Documentation</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            ${offers.map(o => `
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-3 font-semibold text-slate-900">Student #${o.student_id}</td>
                                    <td class="p-3">
                                        <span class="font-medium text-slate-800">${o.company_name}</span>
                                        <span class="block text-slate-400 text-[10px]">${o.role_title}</span>
                                    </td>
                                    <td class="p-3 font-heading font-bold text-emerald-600">₹${o.ctc_lpa} LPA</td>
                                    <td class="p-3 text-slate-500">${o.offer_date}</td>
                                    <td class="p-3">
                                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${o.acceptance_status === 'ACCEPTED' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}">
                                            ${o.acceptance_status}
                                        </span>
                                    </td>
                                    <td class="p-3 text-slate-700">${o.joining_status}</td>
                                    <td class="p-3"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium">${o.documentation_status}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

    } else if (state.adminTab === 'documents') {
        // TAB 6: DOCUMENT VERIFICATION
        const docs = await api('/admin/documents');
        container.innerHTML = `
            <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
                <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                        <h3 class="font-heading font-bold text-lg text-slate-900">Student Document Verification Console</h3>
                        <p class="text-xs text-slate-500">Verify uploaded marksheets, identity proofs, and certifications</p>
                    </div>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 text-slate-600 uppercase text-[10px] font-semibold border-b border-slate-200">
                            <tr>
                                <th class="p-3">Document Title</th>
                                <th class="p-3">Student ID</th>
                                <th class="p-3">Category</th>
                                <th class="p-3">Status</th>
                                <th class="p-3">Verified By</th>
                                <th class="p-3 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            ${docs.map(d => `
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-3 font-semibold text-slate-900">${d.title}</td>
                                    <td class="p-3 text-slate-600">Student #${d.student_id}</td>
                                    <td class="p-3"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px]">${d.doc_type}</span></td>
                                    <td class="p-3">
                                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${d.status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}">
                                            ${d.status}
                                        </span>
                                    </td>
                                    <td class="p-3 text-slate-500">${d.verified_by || 'Pending'}</td>
                                    <td class="p-3 text-right space-x-1">
                                        <button onclick="verifyDocumentStatus(${d.id}, 'VERIFIED')" class="px-2 py-1 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded font-semibold text-[11px]">Verify</button>
                                        <button onclick="verifyDocumentStatus(${d.id}, 'REJECTED')" class="px-2 py-1 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded font-semibold text-[11px]">Reject</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

    } else if (state.adminTab === 'atrisk') {
        // TAB 7: PREDICTIVE AT-RISK MODEL
        const atRiskStudents = await api('/analytics/at-risk');
        container.innerHTML = `
            <div class="space-y-6">
                <div class="p-6 bg-rose-50/60 rounded-2xl border border-rose-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded bg-rose-200 text-rose-900 text-[10px] font-bold uppercase">Predictive ML Model</span>
                            <span class="text-xs text-rose-800 font-medium">Early Risk Detection & Faculty Intervention</span>
                        </div>
                        <h3 class="font-heading font-bold text-xl text-slate-900 mt-1">Students At-Risk of Remaining Unplaced</h3>
                        <p class="text-xs text-slate-600 mt-1">Evaluates low readiness, academic backlogs, poor aptitude/interview scores, and repeated rejection histories.</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${atRiskStudents.filter(s => s.risk_level === 'HIGH' || s.risk_level === 'MEDIUM').map(s => `
                        <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <div class="flex items-start justify-between">
                                    <div>
                                        <h4 class="font-heading font-bold text-base text-slate-900">${s.name}</h4>
                                        <p class="text-slate-400 text-xs">${s.student_roll} • Branch: <b>${s.branch}</b> | CGPA: <b>${s.cgpa}</b></p>
                                    </div>
                                    <span class="px-2.5 py-1 rounded-full text-xs font-bold ${s.risk_level === 'HIGH' ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-amber-100 text-amber-800 border border-amber-300'}">
                                        ${s.risk_level} RISK
                                    </span>
                                </div>

                                <div class="mt-4 space-y-2 text-xs">
                                    <span class="font-semibold text-slate-700 block">Identified Risk Factors:</span>
                                    <ul class="space-y-1 text-slate-600">
                                        ${s.risk_reasons.map(r => `<li class="flex items-start space-x-1.5"><span class="text-rose-500 font-bold">•</span><span>${r}</span></li>`).join('')}
                                    </ul>
                                </div>
                            </div>

                            <div class="mt-4 pt-4 border-t border-slate-100 text-xs">
                                <span class="font-semibold text-indigo-700 block mb-1">Recommended TPO Intervention:</span>
                                <p class="text-slate-600 bg-indigo-50/50 p-2.5 rounded-xl border border-indigo-100">${s.recommended_action}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

async function loadStudentRoster() {
    const tbody = document.getElementById('roster-table-body');
    if (!tbody) return;
    try {
        const students = await api('/students');
        tbody.innerHTML = students.slice(0, 15).map(s => `
            <tr class="hover:bg-slate-50 transition">
                <td class="p-3">
                    <span class="font-semibold text-slate-900 block">${s.name}</span>
                    <span class="text-slate-400 text-[10px]">${s.student_id}</span>
                </td>
                <td class="p-3 text-slate-700 font-medium">${s.branch}</td>
                <td class="p-3 font-semibold text-slate-900">${s.cgpa}</td>
                <td class="p-3">${s.backlogs > 0 ? `<span class="text-rose-600 font-bold">${s.backlogs}</span>` : '0'}</td>
                <td class="p-3">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${getReadinessBadgeClass(s.readiness_class)}">
                        ${s.readiness_score} (${s.readiness_class})
                    </span>
                </td>
                <td class="p-3">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${s.at_risk_level === 'HIGH' ? 'bg-rose-50 text-rose-700' : (s.at_risk_level === 'MEDIUM' ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700')}">
                        ${s.at_risk_level}
                    </span>
                </td>
                <td class="p-3 text-right">
                    <button onclick="navigateTo('student'); renderStudentDashboard(document.getElementById('app-content'), ${s.id})" class="px-2 py-1 rounded bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-medium transition">
                        View Profile
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-rose-500">Error loading roster: ${e.message}</td></tr>`;
    }
}

async function initAnalyticsCharts() {
    try {
        const branchData = await api('/analytics/branches');
        const packageData = await api('/analytics/packages');
        const skillData = await api('/analytics/skills');
        const trendData = await api('/analytics/trend');
        const recruiterData = await api('/analytics/recruiters');

        // 1. Branch Chart
        const bCtx = document.getElementById('branchPlacementChart');
        if (bCtx) {
            new Chart(bCtx, {
                type: 'bar',
                data: {
                    labels: branchData.map(b => b.branch),
                    datasets: [
                        {
                            label: 'Placement %',
                            data: branchData.map(b => b.placement_rate),
                            backgroundColor: 'rgba(99, 102, 241, 0.85)',
                            borderRadius: 6
                        },
                        {
                            label: 'Avg CTC (LPA)',
                            data: branchData.map(b => b.avg_ctc_lpa),
                            backgroundColor: 'rgba(16, 185, 129, 0.85)',
                            borderRadius: 6
                        }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 2. Package Bracket Donut
        const pCtx = document.getElementById('packageDistChart');
        if (pCtx) {
            new Chart(pCtx, {
                type: 'doughnut',
                data: {
                    labels: packageData.map(p => p.bracket),
                    datasets: [{
                        data: packageData.map(p => p.count),
                        backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#ec4899']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 3. Skill Demand Chart
        const sCtx = document.getElementById('skillPlacementChart');
        if (sCtx) {
            new Chart(sCtx, {
                type: 'bar',
                data: {
                    labels: skillData.map(s => s.skill),
                    datasets: [{
                        label: 'Placed Students',
                        data: skillData.map(s => s.placed_count),
                        backgroundColor: 'rgba(14, 165, 233, 0.85)',
                        borderRadius: 6
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y' }
            });
        }

        // 4. Pipeline Funnel
        const fCtx = document.getElementById('pipelineFunnelChart');
        if (fCtx) {
            new Chart(fCtx, {
                type: 'bar',
                data: {
                    labels: trendData.map(t => t.stage),
                    datasets: [{
                        label: 'Candidate Count',
                        data: trendData.map(t => t.count),
                        backgroundColor: 'rgba(168, 85, 247, 0.85)',
                        borderRadius: 6
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Recruiter table
        const rBody = document.getElementById('recruiter-analytics-body');
        if (rBody) {
            rBody.innerHTML = recruiterData.map(r => `
                <tr class="hover:bg-slate-50 transition">
                    <td class="p-3 font-semibold text-slate-900">${r.company_name}</td>
                    <td class="p-3 text-slate-500">${r.industry}</td>
                    <td class="p-3 font-medium">${r.jobs_posted}</td>
                    <td class="p-3 font-semibold text-emerald-600">${r.offers_made}</td>
                    <td class="p-3 font-heading font-bold text-slate-800">₹${r.avg_package_lpa} LPA</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.is_repeat_recruiter ? 'bg-teal-50 text-teal-700' : 'bg-slate-100 text-slate-600'}">${r.is_repeat_recruiter ? 'Repeat Partner' : 'New Recruiter'}</span></td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.error("Failed to render charts:", e);
    }
}

async function runAutoScheduleOptimization() {
    showToast("Running automated sequential schedule optimizer...", 'info');
    try {
        const res = await api('/scheduling/apply-optimization', { method: 'POST' });
        showToast(res.message, 'success');
        switchAdminTab('drives');
    } catch (e) {
        showToast("Optimization failed: " + e.message, 'error');
    }
}

async function updateAppPipelineStage(appId, newStatus) {
    if (!newStatus) return;
    try {
        const res = await api(`/admin/applications/${appId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });
        showToast(res.message, 'success');
        switchAdminTab('pipeline');
    } catch (e) {
        showToast("Update failed: " + e.message, 'error');
    }
}

async function verifyDocumentStatus(docId, newStatus) {
    try {
        const res = await api(`/admin/documents/${docId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus, verified_by: "TPO Central Office" })
        });
        showToast(res.message, 'success');
        switchAdminTab('documents');
    } catch (e) {
        showToast("Action failed: " + e.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 5. AI ASSISTANT CHATBOT
// -------------------------------------------------------------------------------------------------
function toggleChatbot() {
    const win = document.getElementById('chatbot-window');
    win.classList.toggle('hidden');
    if (!win.classList.contains('hidden') && document.getElementById('chatbot-messages').children.length === 0) {
        // Init welcome message
        appendChatMessage('assistant', `Hello! I am your **CAMPUSLINK AI Placement Assistant**.\n\nAsk me about your company eligibility, missing skills, target drive matches, or how to boost your readiness score!`);
    }
}

async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input-text');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    sendChatMessage(msg);
}

async function sendChatMessage(text) {
    appendChatMessage('user', text);
    const win = document.getElementById('chatbot-window');
    if (win.classList.contains('hidden')) win.classList.remove('hidden');

    const loaderId = appendChatLoader();
    try {
        const res = await api('/assistant/chat', {
            method: 'POST',
            body: JSON.stringify({
                message: text,
                student_id: state.currentStudentId || 1
            })
        });
        removeChatLoader(loaderId);
        appendChatMessage('assistant', res.reply);
    } catch (e) {
        removeChatLoader(loaderId);
        appendChatMessage('assistant', "Sorry, I encountered an issue analyzing your placement query: " + e.message);
    }
}

function appendChatMessage(sender, text) {
    const container = document.getElementById('chatbot-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} text-xs`;

    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
                              .replace(/\*(.*?)\*/g, '<i>$1</i>')
                              .replace(/\n/g, '<br>');

    msgDiv.innerHTML = `
        <div class="max-w-[85%] p-3 rounded-2xl ${sender === 'user' ? 'bg-indigo-600 text-white rounded-br-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'}">
            ${formattedText}
        </div>
    `;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function appendChatLoader() {
    const container = document.getElementById('chatbot-messages');
    const id = 'loader-' + Date.now();
    const loaderDiv = document.createElement('div');
    loaderDiv.id = id;
    loaderDiv.className = 'flex justify-start text-xs';
    loaderDiv.innerHTML = `
        <div class="p-2.5 rounded-2xl bg-white border border-slate-200 text-slate-400 flex items-center space-x-1">
            <span class="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce"></span>
            <span class="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 0.15s"></span>
            <span class="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 0.3s"></span>
        </div>
    `;
    container.appendChild(loaderDiv);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeChatLoader(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// -------------------------------------------------------------------------------------------------
// 6. EXPLAINABILITY MODALS
// -------------------------------------------------------------------------------------------------
function showExplainModal(job) {
    const modal = document.getElementById('explain-modal');
    const body = document.getElementById('explain-modal-body');

    body.innerHTML = `
        <div class="space-y-4 text-xs">
            <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold uppercase text-[10px]">Explainable AI Match</span>
            </div>
            <h3 class="font-heading font-extrabold text-xl text-slate-900">${job.title} — ${job.company_name}</h3>
            <div class="p-4 bg-indigo-50/50 rounded-xl border border-indigo-100 flex items-center justify-between">
                <div>
                    <span class="text-xs text-indigo-900 font-semibold block">Hybrid AI Match Score:</span>
                    <span class="font-heading font-black text-2xl text-indigo-600">${job.fit_score}/100</span>
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-bold ${job.is_eligible ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                    ${job.is_eligible ? 'Eligibility Passed' : 'Cutoff Conflict'}
                </span>
            </div>

            <div>
                <span class="font-semibold text-slate-800 block mb-1">Why this score was generated:</span>
                <ul class="space-y-1 text-slate-600">
                    ${(job.positive_reasons || []).map(r => `<li class="flex items-start space-x-1.5"><span class="text-emerald-500 font-bold">✓</span><span>${r}</span></li>`).join('')}
                </ul>
            </div>

            ${(job.missing_skills && job.missing_skills.length > 0) ? `
                <div class="pt-2">
                    <span class="font-semibold text-rose-800 block mb-1">Missing Requirements:</span>
                    <div class="flex flex-wrap gap-1">
                        ${job.missing_skills.map(s => `<span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-medium">✗ ${s}</span>`).join('')}
                    </div>
                </div>
            ` : ''}

            <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span class="font-semibold text-slate-800 block mb-1">Recommendation:</span>
                <p class="text-slate-600">${job.recommendation}</p>
            </div>

            <p class="text-[10px] text-slate-400 italic pt-2 border-t border-slate-100">
                ⚖️ <b>Responsible AI Notice:</b> AI recommendations are decision-support tools and should be reviewed by authorized placement personnel. Personal protected characteristics are never factored into match scoring.
            </p>
        </div>
    `;
    modal.classList.remove('hidden');
    lucide.createIcons();
}

function showCandidateExplainModal(cand, jobTitle) {
    const modal = document.getElementById('explain-modal');
    const body = document.getElementById('explain-modal-body');

    body.innerHTML = `
        <div class="space-y-4 text-xs">
            <span class="px-2 py-0.5 rounded bg-teal-50 text-teal-700 font-bold uppercase text-[10px]">Candidate Audit Breakdown</span>
            <h3 class="font-heading font-extrabold text-xl text-slate-900">${cand.name} (${cand.branch})</h3>
            <p class="text-slate-500">Target Role: <b>${jobTitle}</b></p>

            <div class="p-4 bg-teal-50/50 rounded-xl border border-teal-100 flex items-center justify-between">
                <div>
                    <span class="text-xs text-teal-900 font-semibold block">Hybrid Match Score:</span>
                    <span class="font-heading font-black text-2xl text-teal-600">${cand.fit_score}/100</span>
                </div>
                <div>
                    <span class="text-xs text-slate-500 font-semibold block">Readiness:</span>
                    <span class="font-heading font-bold text-lg text-slate-800">${cand.readiness_score}/100</span>
                </div>
            </div>

            <div>
                <span class="font-semibold text-slate-800 block mb-1">Fit Explanation Factors:</span>
                <ul class="space-y-1 text-slate-600">
                    ${(cand.positive_reasons || []).map(r => `<li class="flex items-start space-x-1.5"><span class="text-emerald-500 font-bold">✓</span><span>${r}</span></li>`).join('')}
                </ul>
            </div>

            ${(cand.missing_skills && cand.missing_skills.length > 0) ? `
                <div class="pt-2">
                    <span class="font-semibold text-rose-800 block mb-1">Candidate Skill Gaps:</span>
                    <div class="flex flex-wrap gap-1">
                        ${cand.missing_skills.map(s => `<span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-medium">✗ ${s}</span>`).join('')}
                    </div>
                </div>
            ` : ''}

            <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span class="font-semibold text-slate-800 block mb-1">AI Recommendation:</span>
                <p class="text-slate-600">${cand.recommendation}</p>
            </div>

            <p class="text-[10px] text-slate-400 italic pt-2 border-t border-slate-100">
                ⚖️ <b>Responsible AI Notice:</b> AI recommendations are decision-support tools and should be reviewed by authorized placement personnel.
            </p>
        </div>
    `;
    modal.classList.remove('hidden');
    lucide.createIcons();
}

function closeExplainModal() {
    document.getElementById('explain-modal').classList.add('hidden');
}

// -------------------------------------------------------------------------------------------------
// 7. NOTIFICATIONS & MODALS
// -------------------------------------------------------------------------------------------------
async function fetchNotifications() {
    try {
        const notifs = await api('/notifications');
        state.notifications = notifs;
        const unread = notifs.filter(n => !n.is_read);
        const badge = document.getElementById('notif-badge');
        if (unread.length > 0) {
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }

        const list = document.getElementById('notif-list');
        if (list) {
            if (notifs.length === 0) {
                list.innerHTML = `<p class="p-4 text-center text-slate-400">No notifications.</p>`;
            } else {
                list.innerHTML = notifs.map(n => `
                    <div class="p-3 ${n.is_read ? 'opacity-70' : 'bg-indigo-50/40'} hover:bg-slate-50 transition">
                        <span class="font-semibold text-slate-900 block">${n.title}</span>
                        <p class="text-slate-600 mt-0.5">${n.message}</p>
                        <span class="text-[9px] text-slate-400 mt-1 block">${new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                `).join('');
            }
        }
    } catch (e) {
        console.error("Notifications fetch error:", e);
    }
}

function toggleNotificationDropdown() {
    document.getElementById('notif-dropdown').classList.toggle('hidden');
}

async function markAllNotificationsRead() {
    try {
        await api('/notifications/read-all', { method: 'PUT' });
        fetchNotifications();
        showToast("All notifications marked as read", 'success');
    } catch (e) {
        console.error(e);
    }
}

function openLoginModal() {
    document.getElementById('login-modal').classList.remove('hidden');
}

function closeLoginModal() {
    document.getElementById('login-modal').classList.add('hidden');
}

async function handleManualLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await api('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        localStorage.setItem('campuslink_token', res.access_token);
        state.token = res.access_token;
        state.currentUser = res;
        closeLoginModal();
        showToast(`Welcome back, ${res.name}!`, 'success');
        await checkAuth();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loginAsPersona(email) {
    showToast(`Signing in as ${email}...`, 'info');
    try {
        const quickUsers = await api('/demo/quick-users');
        const match = quickUsers.find(u => u.email === email);
        if (match) {
            localStorage.setItem('campuslink_token', match.token);
            state.token = match.token;
            state.currentUser = match;
            closeLoginModal();
            showToast(`Logged in as ${match.name}`, 'success');
            await checkAuth();
        } else {
            // fallback standard login
            const res = await api('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password: email.includes('tpo') ? 'admin123' : 'password123' })
            });
            localStorage.setItem('campuslink_token', res.access_token);
            state.token = res.access_token;
            state.currentUser = res;
            closeLoginModal();
            showToast(`Logged in as ${res.name}`, 'success');
            await checkAuth();
        }
    } catch (e) {
        showToast("Login failed: " + e.message, 'error');
    }
}

function logout() {
    localStorage.removeItem('campuslink_token');
    state.token = null;
    state.currentUser = null;
    updateNavAuth();
    navigateTo('landing');
    showToast("Logged out successfully.", 'info');
}

// -------------------------------------------------------------------------------------------------
// 8. HACKATHON DEMO ACTIONS
// -------------------------------------------------------------------------------------------------
async function resetDemoData() {
    if (!confirm("Reset database with complete realistic seed dataset (32 students, 5 recruiters, drives, conflicts)?")) return;
    showToast("Resetting seed data...", 'info');
    try {
        const res = await api('/demo/reset-seed', { method: 'POST' });
        showToast(res.message, 'success');
        navigateTo(state.activeView);
    } catch (e) {
        showToast("Reset failed: " + e.message, 'error');
    }
}

async function triggerQuickConflictDemo() {
    navigateTo('admin');
    switchAdminTab('drives');
    showToast("Opening Intelligent Conflict Detector...", 'info');
}

async function triggerQuickOfferSim() {
    showToast("Simulating fast-track candidate selection & ₹8 LPA offer...", 'info');
    try {
        const res = await api('/demo/simulate-offer', { method: 'POST' });
        showToast(res.message, 'success');
        if (state.activeView === 'student') {
            renderStudentDashboard(document.getElementById('app-content'), 1);
        } else if (state.activeView === 'admin') {
            switchAdminTab('offers');
        }
    } catch (e) {
        showToast("Simulation failed: " + e.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 9. UTILITIES & BADGES
// -------------------------------------------------------------------------------------------------
function getReadinessBadgeClass(cls) {
    switch (cls) {
        case 'Highly Employable': return 'bg-emerald-100 text-emerald-800 border border-emerald-300';
        case 'Ready': return 'bg-indigo-100 text-indigo-800 border border-indigo-300';
        case 'Developing': return 'bg-amber-100 text-amber-800 border border-amber-300';
        default: return 'bg-rose-100 text-rose-800 border border-rose-300';
    }
}

function getPipelineBadgeClass(status) {
    switch (status) {
        case 'JOINED':
        case 'OFFER_ACCEPTED': return 'bg-emerald-100 text-emerald-800 border border-emerald-300';
        case 'SELECTED':
        case 'OFFER_GENERATED': return 'bg-teal-100 text-teal-800 border border-teal-300';
        case 'INTERVIEW': return 'bg-purple-100 text-purple-800 border border-purple-300';
        case 'ASSESSMENT': return 'bg-cyan-100 text-cyan-800 border border-cyan-300';
        case 'AI_SHORTLISTED': return 'bg-indigo-100 text-indigo-800 border border-indigo-300';
        case 'REJECTED': return 'bg-rose-100 text-rose-800 border border-rose-300';
        default: return 'bg-slate-100 text-slate-700 border border-slate-300';
    }
}

// -------------------------------------------------------------------------------------------------
// 10. RECRUITER JOB CREATION & AI JD PARSER
// -------------------------------------------------------------------------------------------------
function openJobCreateModal() {
    document.getElementById('job-create-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeJobCreateModal() {
    document.getElementById('job-create-modal').classList.add('hidden');
}

function autoAnalyzeJD(text) {
    const preview = document.getElementById('jd-extracted-preview');
    if (!text || text.trim().length < 10) {
        preview.textContent = "Type in description above to extract requirements automatically...";
        return;
    }

    // Extract CGPA regex
    const cgpaMatch = text.match(/(?:cgpa|gpa|pointer)[\s:>=]+([0-9]\.?[0-9]*)/i) || text.match(/minimum[\s]+([0-9]\.?[0-9]*)[\s]+cgpa/i);
    if (cgpaMatch) {
        const val = parseFloat(cgpaMatch[1]);
        if (val >= 4.0 && val <= 10.0) {
            document.getElementById('new-job-cgpa').value = val;
        }
    }

    // Extract common branches
    const detectedBranches = [];
    if (/computer science|cse|cs\b/i.test(text)) detectedBranches.push('CSE');
    if (/information technology|\bit\b/i.test(text)) detectedBranches.push('IT');
    if (/electronics|ece\b/i.test(text)) detectedBranches.push('ECE');
    if (/electrical|eee\b/i.test(text)) detectedBranches.push('EEE');
    if (/mechanical|\bme\b/i.test(text)) detectedBranches.push('ME');
    if (/civil/i.test(text)) detectedBranches.push('Civil');

    if (detectedBranches.length > 0) {
        document.getElementById('new-job-branches').value = detectedBranches.join(', ');
    }

    // Extract skills
    const knownSkills = ['Java', 'Spring Boot', 'SQL', 'REST API', 'Git', 'Python', 'React', 'Node.js', 'Docker', 'AWS', 'C++', 'Linux', 'DSA'];
    const detectedSkills = knownSkills.filter(s => new RegExp('\\b' + s.replace('+', '\\+') + '\\b', 'i').test(text));
    if (detectedSkills.length > 0) {
        document.getElementById('new-job-skills').value = detectedSkills.join(', ');
    }

    preview.innerHTML = `<b>Min CGPA:</b> ${document.getElementById('new-job-cgpa').value} | <b>Branches:</b> ${document.getElementById('new-job-branches').value} | <b>Skills:</b> ${document.getElementById('new-job-skills').value}`;
}

async function handleJobCreateSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('new-job-title').value.trim();
    const description = document.getElementById('new-job-description').value.trim();
    const ctc_lpa = parseFloat(document.getElementById('new-job-ctc').value);
    const min_cgpa = parseFloat(document.getElementById('new-job-cgpa').value);
    const branches = document.getElementById('new-job-branches').value.split(',').map(s => s.trim()).filter(Boolean);
    const skills = document.getElementById('new-job-skills').value.split(',').map(s => s.trim()).filter(Boolean);

    showToast("Publishing job with AI matching parameters...", 'info');
    try {
        const res = await api('/jobs', {
            method: 'POST',
            body: JSON.stringify({
                title,
                description,
                min_cgpa,
                ctc_lpa,
                eligible_branches: branches,
                required_skills: skills,
                preferred_skills: ["Docker", "Cloud"],
                required_certifications: []
            })
        });
        showToast(`Role "${res.title}" successfully published to campus placement arena!`, 'success');
        closeJobCreateModal();
        state.selectedJobForMatching = res.id;
        renderRecruiterDashboard(document.getElementById('app-content'));
    } catch (err) {
        showToast("Failed to create job: " + err.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 5. STUDENT PROFILE EDIT HANDLERS
// -------------------------------------------------------------------------------------------------
async function openStudentProfileModal(studentId) {
    try {
        const student = await api(`/students/${studentId}`);
        document.getElementById('edit-student-id').value = student.id;
        document.getElementById('edit-student-phone').value = student.phone || '';
        document.getElementById('edit-student-branch').value = student.branch || 'CSE';
        document.getElementById('edit-student-cgpa').value = student.cgpa || 7.0;
        document.getElementById('edit-student-backlogs').value = student.backlogs || 0;
        
        const skills = JSON.parse(student.technical_skills || '[]');
        document.getElementById('edit-student-skills').value = skills.join(', ');

        const soft = JSON.parse(student.soft_skills || '[]');
        document.getElementById('edit-student-soft-skills').value = soft.join(', ');

        const certs = JSON.parse(student.certifications || '[]');
        document.getElementById('edit-student-certs').value = certs.join(', ');

        document.getElementById('edit-student-internship').value = student.internship_experience || '';

        document.getElementById('student-profile-modal').classList.remove('hidden');
        lucide.createIcons();
    } catch (err) {
        showToast("Failed to load student profile: " + err.message, 'error');
    }
}

function closeStudentProfileModal() {
    document.getElementById('student-profile-modal').classList.add('hidden');
}

async function handleStudentProfileSubmit(e) {
    e.preventDefault();
    const studentId = parseInt(document.getElementById('edit-student-id').value);
    const phone = document.getElementById('edit-student-phone').value.trim();
    const branch = document.getElementById('edit-student-branch').value;
    const cgpa = parseFloat(document.getElementById('edit-student-cgpa').value);
    const backlogs = parseInt(document.getElementById('edit-student-backlogs').value);
    const skills = document.getElementById('edit-student-skills').value.split(',').map(s => s.trim()).filter(Boolean);
    const soft_skills = document.getElementById('edit-student-soft-skills').value.split(',').map(s => s.trim()).filter(Boolean);
    const certifications = document.getElementById('edit-student-certs').value.split(',').map(s => s.trim()).filter(Boolean);
    const internship = document.getElementById('edit-student-internship').value.trim();

    showToast("Updating profile and recalculating readiness score...", 'info');
    try {
        const res = await api(`/students/${studentId}`, {
            method: 'PUT',
            body: JSON.stringify({
                phone,
                branch,
                cgpa,
                backlogs,
                technical_skills: skills,
                soft_skills,
                certifications,
                internship_experience: internship
            })
        });
        showToast(`Profile updated! New Readiness Score: ${res.readiness_score}/100 (${res.readiness_class})`, 'success');
        closeStudentProfileModal();
        renderStudentDashboard(document.getElementById('app-content'), studentId);
    } catch (err) {
        showToast("Profile update failed: " + err.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 6. STUDENT OFFER INTERACTION
// -------------------------------------------------------------------------------------------------
async function respondToOffer(studentId, offerId, action) {
    const actionText = action === 'ACCEPT' ? 'accept' : 'decline';
    if (!confirm(`Are you sure you want to ${actionText} this placement offer?`)) {
        return;
    }
    showToast(`Processing offer ${actionText}...`, 'info');
    try {
        const res = await api(`/students/${studentId}/offers/${offerId}/respond`, {
            method: 'POST',
            body: JSON.stringify({
                action,
                remarks: action === 'ACCEPT' ? 'Accepted by candidate via Student Portal.' : 'Declined by candidate.'
            })
        });
        showToast(res.message, 'success');
        renderStudentDashboard(document.getElementById('app-content'), studentId);
    } catch (err) {
        showToast("Offer action failed: " + err.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 7. INTERVIEW SCHEDULING HANDLERS
// -------------------------------------------------------------------------------------------------
function openScheduleInterviewModal(appId, studentId, studentName, jobTitle) {
    document.getElementById('sched-app-id').value = appId || '';
    document.getElementById('sched-student-id').value = studentId || '';
    document.getElementById('schedule-interview-subtext').textContent = `Candidate: ${studentName} for ${jobTitle}`;
    document.getElementById('schedule-interview-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeScheduleInterviewModal() {
    document.getElementById('schedule-interview-modal').classList.add('hidden');
}

async function handleScheduleInterviewSubmit(e) {
    e.preventDefault();
    const appId = parseInt(document.getElementById('sched-app-id').value);
    const studentId = parseInt(document.getElementById('sched-student-id').value);
    const roundName = document.getElementById('sched-round-name').value.trim();
    const scheduledTime = document.getElementById('sched-time').value.trim();
    const panel = document.getElementById('sched-panel').value.trim();

    showToast("Scheduling interview and notifying candidate...", 'info');
    try {
        const res = await api('/interviews', {
            method: 'POST',
            body: JSON.stringify({
                application_id: appId,
                student_id: studentId,
                round_name: roundName,
                scheduled_time: scheduledTime,
                interviewer_panel: panel,
                status: 'SCHEDULED'
            })
        });
        showToast(`Interview round "${res.round_name}" successfully scheduled! Notification sent.`, 'success');
        closeScheduleInterviewModal();
        if (state.activeView === 'recruiter') {
            renderRecruiterDashboard(document.getElementById('app-content'));
        } else if (state.activeView === 'admin') {
            renderAdminDashboard(document.getElementById('app-content'));
        }
    } catch (err) {
        showToast("Scheduling interview failed: " + err.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 8. INTERVIEW FEEDBACK & EVALUATION HANDLERS
// -------------------------------------------------------------------------------------------------
function openInterviewFeedbackModal(interviewId, studentName, roundName, techRating = 8.0, commRating = 7.5, recommendation = 'PROGRESS', feedback = '') {
    document.getElementById('feedback-interview-id').value = interviewId;
    document.getElementById('feedback-modal-subtext').textContent = `Candidate: ${studentName} • Round: ${roundName}`;
    document.getElementById('feedback-tech-rating').value = techRating || 8.0;
    document.getElementById('feedback-comm-rating').value = commRating || 7.5;
    document.getElementById('feedback-rec').value = recommendation || 'PROGRESS';
    document.getElementById('feedback-notes').value = feedback || '';
    document.getElementById('interview-feedback-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeInterviewFeedbackModal() {
    document.getElementById('interview-feedback-modal').classList.add('hidden');
}

async function handleInterviewFeedbackSubmit(e) {
    e.preventDefault();
    const interviewId = parseInt(document.getElementById('feedback-interview-id').value);
    const techRating = parseFloat(document.getElementById('feedback-tech-rating').value);
    const commRating = parseFloat(document.getElementById('feedback-comm-rating').value);
    const statusVal = document.getElementById('feedback-status').value;
    const recommendation = document.getElementById('feedback-rec').value;
    const feedback = document.getElementById('feedback-notes').value.trim();

    showToast("Saving evaluation and updating candidate pipeline...", 'info');
    try {
        const res = await api(`/interviews/${interviewId}`, {
            method: 'PUT',
            body: JSON.stringify({
                technical_rating: techRating,
                comm_rating: commRating,
                status: statusVal,
                recommendation: recommendation,
                feedback: feedback
            })
        });
        showToast(`Evaluation recorded! Recommendation: ${res.recommendation}. Candidate notified.`, 'success');
        closeInterviewFeedbackModal();
        if (state.activeView === 'recruiter') {
            renderRecruiterDashboard(document.getElementById('app-content'));
        } else if (state.activeView === 'admin') {
            renderAdminDashboard(document.getElementById('app-content'));
        }
    } catch (err) {
        showToast("Failed to save evaluation: " + err.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 9. PLACEMENT DRIVE CREATION HANDLERS
// -------------------------------------------------------------------------------------------------
function openCreateDriveModal() {
    document.getElementById('create-drive-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeCreateDriveModal() {
    document.getElementById('create-drive-modal').classList.add('hidden');
}

async function handleCreateDriveSubmit(e) {
    e.preventDefault();
    const compName = document.getElementById('drive-comp-name').value.trim();
    const roleTitle = document.getElementById('drive-role-title').value.trim();
    const driveDate = document.getElementById('drive-date').value.trim();
    const startTime = document.getElementById('drive-start-time').value.trim();
    const endTime = document.getElementById('drive-end-time').value.trim();
    const venue = document.getElementById('drive-venue').value;
    const panel = document.getElementById('drive-panel').value;
    const eligibility = document.getElementById('drive-eligibility').value.trim();

    showToast("Scheduling placement drive & auditing conflicts...", 'info');
    try {
        const res = await api('/scheduling/drives', {
            method: 'POST',
            body: JSON.stringify({
                company_name: compName,
                role_title: roleTitle,
                drive_date: driveDate,
                start_time: startTime,
                end_time: endTime,
                venue: venue,
                panel_name: panel,
                eligibility_criteria: eligibility
            })
        });
        showToast(`Drive for "${res.company_name}" successfully scheduled at ${res.venue}!`, 'success');
        closeCreateDriveModal();
        renderAdminDashboard(document.getElementById('app-content'));
    } catch (err) {
        showToast("Drive creation failed: " + err.message, 'error');
    }
}

// -------------------------------------------------------------------------------------------------
// 10. PLACEMENT OFFER CREATION HANDLERS
// -------------------------------------------------------------------------------------------------
function openCreateOfferModal(appId = null, studentId = 1, studentName = 'Candidate', compName = 'TechNova Solutions', roleTitle = 'Software Engineer') {
    document.getElementById('offer-app-id').value = appId || '';
    document.getElementById('offer-student-id').value = studentId || 1;
    document.getElementById('offer-modal-subtext').textContent = `Recipient: ${studentName}`;
    document.getElementById('offer-comp-name').value = compName || 'TechNova Solutions';
    document.getElementById('offer-role-title').value = roleTitle || 'Software Engineer';
    document.getElementById('create-offer-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeCreateOfferModal() {
    document.getElementById('create-offer-modal').classList.add('hidden');
}

async function handleCreateOfferSubmit(e) {
    e.preventDefault();
    const appId = document.getElementById('offer-app-id').value ? parseInt(document.getElementById('offer-app-id').value) : null;
    const studentId = parseInt(document.getElementById('offer-student-id').value);
    const compName = document.getElementById('offer-comp-name').value.trim();
    const roleTitle = document.getElementById('offer-role-title').value.trim();
    const ctc = parseFloat(document.getElementById('offer-ctc').value);
    const joiningDate = document.getElementById('offer-joining-date').value.trim();
    const remarks = document.getElementById('offer-remarks').value.trim();

    showToast("Generating official placement offer...", 'info');
    try {
        const res = await api('/admin/offers', {
            method: 'POST',
            body: JSON.stringify({
                application_id: appId,
                student_id: studentId,
                company_name: compName,
                role_title: roleTitle,
                ctc_lpa: ctc,
                offer_date: new Date().toISOString().split('T')[0],
                joining_date: joiningDate,
                remarks: remarks
            })
        });
        showToast(`Official offer letter of ₹${res.ctc_lpa} LPA issued to Student #${res.student_id}! Notification sent.`, 'success');
        closeCreateOfferModal();
        if (state.activeView === 'admin') {
            renderAdminDashboard(document.getElementById('app-content'));
        }
    } catch (err) {
        showToast("Offer generation failed: " + err.message, 'error');
    }
}

