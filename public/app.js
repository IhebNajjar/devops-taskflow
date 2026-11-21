/**
 * TaskFlow Frontend Application Logic
 * Supports:
 * - Real User Authentication (Sign In, Sign Up, Quick 1-Click Demo Login, Log Out)
 * - Hierarchical Project Tasks with Subtasks inside (Checklist, Progress Bar, Add/Delete Subtask)
 * - AI 120B Project Breakdown directly into Big Tasks with Subtasks
 * - Web Audio API Sound Effects & Confetti Celebration
 * - Time Horizon Filters & Psychology XP Rewards
 */

// ==================== SOUND EFFECTS ENGINE (Web Audio API) ====================
const SoundEngine = {
    ctx: null,
    enabled: true,

    init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) this.ctx = new AudioCtx();
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    },

    toggle() {
        this.init();
        this.enabled = !this.enabled;
        const soundIcon = document.getElementById('soundIcon');
        if (this.enabled) {
            soundIcon.className = 'fa-solid fa-volume-high';
            this.playTestSound();
            showToast('🔊 Sound Effects: Enabled (Test Chime Played)', 'info');
        } else {
            soundIcon.className = 'fa-solid fa-volume-xmark';
            showToast('🔇 Sound Effects: Muted', 'info');
        }
        return this.enabled;
    },

    playTestSound() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') this.ctx.resume();

        const now = this.ctx.currentTime + 0.02;
        [587.33, 880.00].forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + idx * 0.12);

            gain.gain.setValueAtTime(0.001, now + idx * 0.12);
            gain.gain.linearRampToValueAtTime(0.45, now + idx * 0.12 + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.12 + 0.35);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + idx * 0.12);
            osc.stop(now + idx * 0.12 + 0.38);
        });
    },

    playComplete() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') this.ctx.resume();

        const now = this.ctx.currentTime + 0.02;
        const notes = [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, now + idx * 0.09);

            gain.gain.setValueAtTime(0.001, now + idx * 0.09);
            gain.gain.linearRampToValueAtTime(0.4, now + idx * 0.09 + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.45);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + idx * 0.09);
            osc.stop(now + idx * 0.09 + 0.48);
        });
    },

    playSubtaskDone() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') this.ctx.resume();

        const now = this.ctx.currentTime + 0.01;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(659.25, now);
        osc.frequency.exponentialRampToValueAtTime(987.77, now + 0.14);

        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.35, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.26);
    },

    playAI() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') this.ctx.resume();

        const now = this.ctx.currentTime + 0.02;
        const freqs = [440, 554.37, 659.25, 880, 1108.73, 1318.51];
        freqs.forEach((f, i) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(f, now + i * 0.06);

            gain.gain.setValueAtTime(0.001, now + i * 0.06);
            gain.gain.linearRampToValueAtTime(0.3, now + i * 0.06 + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.4);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now + i * 0.06);
            osc.stop(now + i * 0.06 + 0.42);
        });
    },

    playClick() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') this.ctx.resume();

        const now = this.ctx.currentTime + 0.01;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(750, now);
        osc.frequency.exponentialRampToValueAtTime(250, now + 0.04);

        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.045);
    }
};

// Global audio unlock on first user gesture
['click', 'pointerdown', 'keydown', 'touchstart'].forEach(evt => {
    window.addEventListener(evt, () => SoundEngine.init(), { passive: true, once: false });
});

// ==================== CONFETTI PARTICLES ====================
const Confetti = {
    canvas: null,
    ctx: null,
    particles: [],
    animId: null,

    init() {
        this.canvas = document.getElementById('confettiCanvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        window.addEventListener('resize', () => this.resize());
    },

    resize() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    },

    burst() {
        this.init();
        if (!this.ctx) return;

        const colors = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'];
        this.particles = [];

        for (let i = 0; i < 90; i++) {
            this.particles.push({
                x: window.innerWidth / 2,
                y: window.innerHeight / 2 - 50,
                vx: (Math.random() - 0.5) * 16,
                vy: (Math.random() - 0.8) * 16,
                size: Math.random() * 8 + 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                rotation: Math.random() * 360,
                vRot: (Math.random() - 0.5) * 10,
                gravity: 0.35,
                opacity: 1
            });
        }

        if (this.animId) cancelAnimationFrame(this.animId);
        this.render();
    },

    render() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        let activeCount = 0;
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.vy += p.gravity;
            p.rotation += p.vRot;
            p.opacity -= 0.012;

            if (p.opacity > 0) {
                activeCount++;
                this.ctx.save();
                this.ctx.translate(p.x, p.y);
                this.ctx.rotate((p.rotation * Math.PI) / 180);
                this.ctx.globalAlpha = Math.max(0, p.opacity);
                this.ctx.fillStyle = p.color;
                this.ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
                this.ctx.restore();
            }
        });

        if (activeCount > 0) {
            this.animId = requestAnimationFrame(() => this.render());
        } else {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
};

// ==================== APPLICATION STATE ====================
let currentUser = { id: 1, username: 'Demo User', xp: 250, streak: 3 };
let allTasks = [];
let taskToDeleteId = null;
let currentPeriod = 'all';
let isLocalOnly = window.location.protocol === 'file:';
let generatedAITasks = [];
let activeAuthTab = 'login';
let openSubtaskCards = new Set(); // Stores task IDs that have subtasks expanded

const MOTIVATION_QUOTES = [
    "Break big goals down into small daily steps!",
    "Focus on one small subtask right now and build momentum.",
    "A massive project is simply 5 to 10 small subtasks done well.",
    "Every milestone you check off compounds into huge success!",
    "Progress over perfection — one subtask at a time."
];

// DOM Elements
const tasksGrid = document.getElementById('tasksGrid');
const emptyState = document.getElementById('emptyState');
const tasksCountBadge = document.getElementById('tasksCountBadge');

// Auth DOM
const authContainer = document.getElementById('authContainer');
const btnAuthOpen = document.getElementById('btnAuthOpen');
const btnLogout = document.getElementById('btnLogout');
const currentUserName = document.getElementById('currentUserName');
const authModal = document.getElementById('authModal');
const btnCloseAuthModal = document.getElementById('btnCloseAuthModal');
const tabLogin = document.getElementById('tabLogin');
const tabRegister = document.getElementById('tabRegister');
const authForm = document.getElementById('authForm');
const authUsername = document.getElementById('authUsername');
const authPassword = document.getElementById('authPassword');
const btnAuthSubmit = document.getElementById('btnAuthSubmit');
const btnQuickDemoLogin = document.getElementById('btnQuickDemoLogin');

// Gamification & Header Elements
const btnToggleSound = document.getElementById('btnToggleSound');
const levelLabel = document.getElementById('levelLabel');
const xpLabel = document.getElementById('xpLabel');
const streakCount = document.getElementById('streakCount');
const floatingXpContainer = document.getElementById('floatingXpContainer');

// Motivation & Summary
const motivationQuote = document.getElementById('motivationQuote');
const sumCompleted = document.getElementById('sumCompleted');
const sumMissing = document.getElementById('sumMissing');
const sumUrgent = document.getElementById('sumUrgent');

// Stats Elements
const statTotal = document.getElementById('statTotal');
const statPending = document.getElementById('statPending');
const statInProgress = document.getElementById('statInProgress');
const statCompleted = document.getElementById('statCompleted');
const progressPercent = document.getElementById('progressPercent');
const progressBar = document.getElementById('progressBar');

// Filters & Time Tabs
const timeTabs = document.querySelectorAll('.time-tab');
const searchInput = document.getElementById('searchInput');
const btnClearSearch = document.getElementById('btnClearSearch');
const filterStatus = document.getElementById('filterStatus');
const filterPriority = document.getElementById('filterPriority');
const filterCategory = document.getElementById('filterCategory');
const btnResetDemo = document.getElementById('btnResetDemo');

// Project Modal
const taskModal = document.getElementById('taskModal');
const deleteModal = document.getElementById('deleteModal');
const btnOpenAddModal = document.getElementById('btnOpenAddModal');
const btnCloseModal = document.getElementById('btnCloseModal');
const btnCancelModal = document.getElementById('btnCancelModal');
const taskForm = document.getElementById('taskForm');
const modalTitle = document.getElementById('modalTitle');
const btnEmptyAdd = document.getElementById('btnEmptyAdd');
const initialSubtasksGroup = document.getElementById('initialSubtasksGroup');
const taskInitialSubtasks = document.getElementById('taskInitialSubtasks');

// AI Modal Elements
const aiModal = document.getElementById('aiModal');
const btnOpenAIModal = document.getElementById('btnOpenAIModal');
const btnEmptyAI = document.getElementById('btnEmptyAI');
const btnCloseAIModal = document.getElementById('btnCloseAIModal');
const btnCancelAI = document.getElementById('btnCancelAI');
const aiProjectInput = document.getElementById('aiProjectInput');
const aiHorizonSelect = document.getElementById('aiHorizonSelect');
const aiCustomDaysInput = document.getElementById('aiCustomDaysInput');
const aiStepsSelect = document.getElementById('aiStepsSelect');
const aiCustomStepsInput = document.getElementById('aiCustomStepsInput');
const btnGenerateAI = document.getElementById('btnGenerateAI');
const aiLoading = document.getElementById('aiLoading');
const aiResultsContainer = document.getElementById('aiResultsContainer');
const aiTasksList = document.getElementById('aiTasksList');
const aiTasksCount = document.getElementById('aiTasksCount');
const btnAddAIStep = document.getElementById('btnAddAIStep');
const btnImportAITasks = document.getElementById('btnImportAITasks');

// Form Inputs
const taskIdInput = document.getElementById('taskId');
const taskTitleInput = document.getElementById('taskTitle');
const taskCategoryInput = document.getElementById('taskCategory');
const taskPriorityInput = document.getElementById('taskPriority');
const taskStatusInput = document.getElementById('taskStatus');
const taskDueDateInput = document.getElementById('taskDueDate');
const taskDescriptionInput = document.getElementById('taskDescription');

// Delete Modal Buttons
const btnCancelDelete = document.getElementById('btnCancelDelete');
const btnConfirmDelete = document.getElementById('btnConfirmDelete');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initAuthAndStorage();
    loadData();
    setupEventListeners();
    updateMotivationQuote();
});

function initAuthAndStorage() {
    const savedUser = localStorage.getItem('taskflow_user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
        } catch {
            currentUser = { id: 1, username: 'Demo User', xp: 250, streak: 3 };
        }
    }
    updateUserUI();
}

function updateUserUI() {
    if (currentUserName) currentUserName.textContent = currentUser.username;
    if (levelLabel) {
        const lvl = 1 + Math.floor((currentUser.xp || 150) / 100);
        levelLabel.textContent = `Lvl. ${lvl}`;
    }
    if (xpLabel) xpLabel.textContent = `${currentUser.xp || 150} XP`;
    if (streakCount) streakCount.textContent = `${currentUser.streak || 2} d`;
}

function updateMotivationQuote() {
    const randomQuote = MOTIVATION_QUOTES[Math.floor(Math.random() * MOTIVATION_QUOTES.length)];
    if (motivationQuote) motivationQuote.textContent = randomQuote;
}

// Setup Event Listeners
function setupEventListeners() {
    btnToggleSound.addEventListener('click', () => SoundEngine.toggle());

    // Auth Listeners
    btnAuthOpen.addEventListener('click', () => {
        SoundEngine.playClick();
        openAuthModal();
    });
    btnLogout.addEventListener('click', () => {
        SoundEngine.playClick();
        handleLogout();
    });
    btnCloseAuthModal.addEventListener('click', closeAuthModal);
    tabLogin.addEventListener('click', () => switchAuthTab('login'));
    tabRegister.addEventListener('click', () => switchAuthTab('register'));
    authForm.addEventListener('submit', handleAuthSubmit);
    btnQuickDemoLogin.addEventListener('click', handleQuickDemoLogin);

    // Time Horizon Tabs
    timeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            timeTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentPeriod = tab.getAttribute('data-period');
            SoundEngine.playClick();
            fetchTasks();
        });
    });

    // Search & Filters
    searchInput.addEventListener('input', handleFilterChange);
    btnClearSearch.addEventListener('click', () => {
        searchInput.value = '';
        btnClearSearch.classList.add('hidden');
        handleFilterChange();
    });

    filterStatus.addEventListener('change', handleFilterChange);
    filterPriority.addEventListener('change', handleFilterChange);
    filterCategory.addEventListener('change', handleFilterChange);

    btnResetDemo.addEventListener('click', resetDemoData);

    // Project Modal
    btnOpenAddModal.addEventListener('click', () => {
        SoundEngine.playClick();
        openModal();
    });
    btnEmptyAdd.addEventListener('click', () => {
        SoundEngine.playClick();
        openModal();
    });
    btnCloseModal.addEventListener('click', closeModal);
    btnCancelModal.addEventListener('click', closeModal);

    taskForm.addEventListener('submit', handleFormSubmit);

    // Delete Modal
    btnCancelDelete.addEventListener('click', closeDeleteModal);
    btnConfirmDelete.addEventListener('click', confirmDelete);

    // AI Assistant Handlers
    btnOpenAIModal.addEventListener('click', openAIModal);
    if (btnEmptyAI) btnEmptyAI.addEventListener('click', openAIModal);
    btnCloseAIModal.addEventListener('click', closeAIModal);
    btnCancelAI.addEventListener('click', closeAIModal);
    btnGenerateAI.addEventListener('click', handleAIGenerate);
    btnImportAITasks.addEventListener('click', handleAIImport);

    if (btnAddAIStep) {
        btnAddAIStep.addEventListener('click', addExtraAIStep);
    }

    aiHorizonSelect.addEventListener('change', () => {
        if (aiHorizonSelect.value === 'custom') {
            aiCustomDaysInput.classList.remove('hidden');
            aiCustomDaysInput.focus();
        } else {
            aiCustomDaysInput.classList.add('hidden');
        }
    });

    aiStepsSelect.addEventListener('change', () => {
        if (aiStepsSelect.value === 'custom') {
            aiCustomStepsInput.classList.remove('hidden');
            aiCustomStepsInput.focus();
        } else {
            aiCustomStepsInput.classList.add('hidden');
        }
    });

    // Close modals on click outside
    window.addEventListener('click', (e) => {
        if (e.target === taskModal) closeModal();
        if (e.target === deleteModal) closeDeleteModal();
        if (e.target === aiModal) closeAIModal();
        if (e.target === authModal) closeAuthModal();
    });
}

// ==================== AUTH LOGIC ====================
function openAuthModal() {
    authModal.classList.remove('hidden');
    switchAuthTab('login');
    authUsername.focus();
}

function closeAuthModal() {
    authModal.classList.add('hidden');
}

function switchAuthTab(tab) {
    activeAuthTab = tab;
    if (tab === 'login') {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        btnAuthSubmit.textContent = 'Sign In';
    } else {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        btnAuthSubmit.textContent = 'Create Account';
    }
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    SoundEngine.playClick();

    const username = authUsername.value.trim();
    const password = authPassword.value.trim();

    if (!username || !password) {
        showToast('Please fill in both fields', 'error');
        return;
    }

    const endpoint = activeAuthTab === 'login' ? '/api/auth/login' : '/api/auth/register';

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Authentication failed');
        }

        currentUser = {
            id: data.id,
            username: data.username,
            xp: data.xp || 150,
            streak: data.streak || 1
        };
        localStorage.setItem('taskflow_user', JSON.stringify(currentUser));

        closeAuthModal();
        updateUserUI();
        SoundEngine.playComplete();
        showToast(`🎉 ${data.message}`, 'success');
        loadData();

    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleQuickDemoLogin() {
    SoundEngine.playClick();
    authUsername.value = 'demo';
    authPassword.value = 'demo123';
    switchAuthTab('login');
    handleAuthSubmit(new Event('submit'));
}

function handleLogout() {
    currentUser = { id: 1, username: 'Demo User', xp: 150, streak: 1 };
    localStorage.removeItem('taskflow_user');
    updateUserUI();
    showToast('Logged out. Switched to demo session.', 'info');
    loadData();
}

// ==================== LOAD & RENDER TASKS ====================
async function loadData() {
    await Promise.all([fetchTasks(), fetchStats()]);
}

function normalizeStatus(s) {
    if (s === 'Completed' || s === 'Terminée') return 'Completed';
    if (s === 'In Progress' || s === 'En cours') return 'In Progress';
    return 'To Do';
}

function normalizePriority(p) {
    if (p === 'High' || p === 'Haute') return 'High';
    if (p === 'Low' || p === 'Basse') return 'Low';
    return 'Medium';
}

function normalizeCategory(c) {
    if (c === 'Development' || c === 'Développement') return 'Development';
    if (c === 'Studies' || c === 'Études') return 'Studies';
    if (c === 'Personal' || c === 'Personnel') return 'Personal';
    return 'Work';
}

async function fetchTasks() {
    const searchVal = searchInput.value.trim().toLowerCase();
    const statusVal = filterStatus.value;
    const prioVal = filterPriority.value;
    const catVal = filterCategory.value;

    try {
        const params = new URLSearchParams();
        if (searchVal) params.append('search', searchVal);
        if (statusVal !== 'All') params.append('status', statusVal);
        if (prioVal !== 'All') params.append('priority', prioVal);
        if (catVal !== 'All') params.append('category', catVal);
        if (currentPeriod !== 'all') params.append('period', currentPeriod);
        if (currentUser.id) params.append('user_id', currentUser.id);

        const res = await fetch(`/api/tasks?${params.toString()}`);
        if (res.ok) {
            allTasks = await res.json();
            renderTasks(allTasks);
            return;
        }
    } catch {
        // Fallback
    }
}

async function fetchStats() {
    try {
        const res = await fetch(`/api/stats?user_id=${currentUser.id || 1}`);
        if (res.ok) {
            const stats = await res.json();
            renderStats(stats);
            if (stats.profile) {
                currentUser.xp = stats.profile.xp;
                currentUser.streak = stats.profile.streak;
                updateUserUI();
            }
        }
    } catch (e) {
        console.error(e);
    }
}

function renderStats(stats) {
    statTotal.textContent = stats.total;
    statPending.textContent = stats.pending;
    statInProgress.textContent = stats.in_progress;
    statCompleted.textContent = stats.completed;

    sumCompleted.textContent = stats.completed;
    sumMissing.textContent = stats.missing !== undefined ? stats.missing : (stats.pending + stats.in_progress);
    sumUrgent.textContent = stats.urgent !== undefined ? stats.urgent : 0;

    progressPercent.textContent = `${stats.completion_rate}%`;
    progressBar.style.width = `${stats.completion_rate}%`;
}

// Render Project Cards with Nested Subtasks
function renderTasks(tasks) {
    tasksGrid.innerHTML = '';
    tasksCountBadge.textContent = tasks.length;

    if (tasks.length === 0) {
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    tasks.forEach(task => {
        const card = document.createElement('div');
        const normStatus = normalizeStatus(task.status);
        const normPriority = normalizePriority(task.priority);
        const normCategory = normalizeCategory(task.category);

        const isCompleted = normStatus === 'Completed';
        card.className = `task-card ${isCompleted ? 'is-completed' : ''}`;

        let prioClass = 'badge-prio-medium';
        if (normPriority === 'High') prioClass = 'badge-prio-high';
        else if (normPriority === 'Low') prioClass = 'badge-prio-low';

        const isOverdue = checkIsOverdue(task.due_date, normStatus);
        const subtasks = task.subtasks || [];
        const subCount = subtasks.length;
        const subDone = subtasks.filter(s => normalizeStatus(s.status) === 'Completed').length;
        const subProgress = subCount > 0 ? Math.round((subDone / subCount) * 100) : (isCompleted ? 100 : 0);
        
        // Auto expand if opened before
        const isExpanded = openSubtaskCards.has(task.id) || subCount > 0;

        card.innerHTML = `
            <div>
                <div class="task-card-header">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <button class="btn-quick-check ${isCompleted ? 'is-checked' : ''}" 
                                onclick="quickToggleComplete(${task.id}, ${!isCompleted}, event)" 
                                title="${isCompleted ? 'Mark as To Do' : 'Mark Project as Completed (+50 XP!)'}">
                            <i class="fa-solid fa-check"></i>
                        </button>
                        <span class="badge badge-cat">${escapeHtml(normCategory)}</span>
                    </div>
                    <span class="badge ${prioClass}">
                        <i class="fa-solid fa-flag"></i> ${escapeHtml(normPriority)}
                    </span>
                </div>

                <h3 class="task-card-title">${escapeHtml(task.title)}</h3>
                <p class="task-card-desc">${escapeHtml(task.description || 'No description provided.')}</p>

                <!-- Subtasks Accordion & Progress inside Card -->
                <div class="subtasks-wrapper">
                    <div class="subtasks-header" onclick="toggleSubtasksView(${task.id})">
                        <span>
                            <i class="fa-solid ${isExpanded ? 'fa-chevron-down' : 'fa-chevron-right'}"></i> 
                            Subtasks (${subDone}/${subCount})
                        </span>
                        <span style="font-size: 0.78rem; color: var(--primary); font-weight: 700;">${subProgress}%</span>
                    </div>

                    <div class="subtasks-progress-mini">
                        <div class="subtasks-progress-fill" style="width: ${subProgress}%;"></div>
                    </div>

                    <div id="subtasksList_${task.id}" class="subtasks-list ${isExpanded ? '' : 'hidden'}">
                        ${renderSubtasksHTML(task.id, subtasks)}

                        <!-- Add subtask inside card -->
                        <div class="subtask-add-row" onclick="event.stopPropagation();">
                            <input type="text" id="newSubtaskInput_${task.id}" placeholder="+ Add small subtask..." 
                                   onkeydown="if(event.key === 'Enter'){ handleAddSubtask(${task.id}); event.preventDefault(); }">
                            <button type="button" class="btn btn-primary" onclick="handleAddSubtask(${task.id})">
                                Add
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="task-card-meta">
                <div class="due-date ${isOverdue ? 'overdue' : ''}">
                    <i class="fa-regular fa-calendar"></i>
                    <span>${task.due_date ? formatDate(task.due_date) : 'No deadline'}</span>
                    ${isOverdue ? '<span title="Deadline has passed">(Overdue)</span>' : ''}
                </div>

                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <select class="status-select ${getStatusClass(normStatus)}" onchange="handleTaskStatusChange(${task.id}, this.value, event)">
                        <option value="To Do" ${normStatus === 'To Do' ? 'selected' : ''}>To Do</option>
                        <option value="In Progress" ${normStatus === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Completed" ${normStatus === 'Completed' ? 'selected' : ''}>Completed</option>
                    </select>

                    <div class="task-card-actions">
                        <button class="btn-icon" title="Edit Project" onclick="editTask(${task.id})">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn-icon delete" title="Delete Project" onclick="openDeleteModal(${task.id})">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        tasksGrid.appendChild(card);
    });
}

function renderSubtasksHTML(taskId, subtasks) {
    if (subtasks.length === 0) {
        return `<p style="font-size: 0.75rem; color: var(--text-muted); font-style: italic; padding: 0.2rem 0;">No subtasks yet. Add one below!</p>`;
    }

    return subtasks.map(s => {
        const isDone = normalizeStatus(s.status) === 'Completed';
        return `
            <div class="subtask-item ${isDone ? 'is-completed' : ''}" onclick="event.stopPropagation();">
                <div class="subtask-left">
                    <button class="subtask-check ${isDone ? 'checked' : ''}" 
                            onclick="toggleSubtaskStatus(${s.id}, ${!isDone}, ${taskId})" 
                            title="${isDone ? 'Mark as To Do' : 'Mark as done (+25 XP!)'}">
                        <i class="fa-solid fa-check"></i>
                    </button>
                    <span class="subtask-title">${escapeHtml(s.title)}</span>
                </div>
                <button class="btn-ai-remove" onclick="handleDeleteSubtask(${s.id})" title="Delete subtask">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>
        `;
    }).join('');
}

function toggleSubtasksView(taskId) {
    if (openSubtaskCards.has(taskId)) {
        openSubtaskCards.delete(taskId);
    } else {
        openSubtaskCards.add(taskId);
    }
    const list = document.getElementById(`subtasksList_${taskId}`);
    if (list) list.classList.toggle('hidden');
}

// Toggle Individual Subtask Status
async function toggleSubtaskStatus(subtaskId, markDone, parentTaskId) {
    const newStatus = markDone ? 'Completed' : 'To Do';

    if (markDone) {
        SoundEngine.playSubtaskDone();
        Confetti.burst();
        showFloatingXp(null, '+25 XP!');
        currentUser.xp = (currentUser.xp || 150) + 25;
        updateUserUI();
    } else {
        SoundEngine.playClick();
    }

    try {
        const res = await fetch(`/api/subtasks/${subtaskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (res.ok) {
            showToast(markDone ? '🎯 Subtask finished! +25 XP!' : 'Subtask updated', 'success');
            openSubtaskCards.add(parentTaskId);
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Add Subtask inside a card
async function handleAddSubtask(taskId) {
    const input = document.getElementById(`newSubtaskInput_${taskId}`);
    if (!input) return;
    const title = input.value.trim();
    if (!title) return;

    SoundEngine.playClick();

    try {
        const res = await fetch(`/api/tasks/${taskId}/subtasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });

        if (res.ok) {
            input.value = '';
            openSubtaskCards.add(taskId);
            showToast('Subtask added!', 'success');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Delete Subtask
async function handleDeleteSubtask(subtaskId) {
    SoundEngine.playClick();
    try {
        const res = await fetch(`/api/subtasks/${subtaskId}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Subtask deleted', 'info');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function quickToggleComplete(id, markDone, event) {
    if (event) event.stopPropagation();
    handleTaskStatusChange(id, markDone ? 'Completed' : 'To Do', event);
}

// Task Status Change
async function handleTaskStatusChange(id, newStatus, event) {
    if (newStatus === 'Completed') {
        SoundEngine.playComplete();
        Confetti.burst();
        showFloatingXp(event, '+50 XP!');
        currentUser.xp = (currentUser.xp || 150) + 50;
        updateUserUI();
    } else {
        SoundEngine.playClick();
    }

    try {
        const res = await fetch(`/api/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (res.ok) {
            showToast(newStatus === 'Completed' ? '🎉 Project Completed! +50 XP!' : 'Status updated!', 'success');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function showFloatingXp(event, text = '+50 XP!') {
    const el = document.createElement('div');
    el.className = 'floating-xp';
    el.innerHTML = `<i class="fa-solid fa-star"></i> ${text}`;
    floatingXpContainer.appendChild(el);
    setTimeout(() => el.remove(), 1200);
}

function getStatusClass(status) {
    if (status === 'Completed' || status === 'Terminée') return 'stat-completed';
    if (status === 'In Progress' || status === 'En cours') return 'stat-inprogress';
    return 'stat-todo';
}

function checkIsOverdue(dueDate, status) {
    if (!dueDate || status === 'Completed' || status === 'Terminée') return false;
    const today = new Date().toISOString().split('T')[0];
    return dueDate < today;
}

function formatDate(dateStr) {
    try {
        const parts = dateStr.split('-');
        if (parts.length === 3) {
            const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const monthIdx = parseInt(parts[1], 10) - 1;
            return `${months[monthIdx]} ${parseInt(parts[2], 10)}, ${parts[0]}`;
        }
        return dateStr;
    } catch {
        return dateStr;
    }
}

function handleFilterChange() {
    if (searchInput.value.trim().length > 0) {
        btnClearSearch.classList.remove('hidden');
    } else {
        btnClearSearch.classList.add('hidden');
    }
    fetchTasks();
}

// Open Add / Edit Modal
function openModal(task = null) {
    taskForm.reset();
    if (task) {
        modalTitle.textContent = 'Edit Project';
        taskIdInput.value = task.id;
        taskTitleInput.value = task.title;
        taskCategoryInput.value = normalizeCategory(task.category);
        taskPriorityInput.value = normalizePriority(task.priority);
        taskStatusInput.value = normalizeStatus(task.status);
        taskDueDateInput.value = task.due_date || '';
        taskDescriptionInput.value = task.description || '';
        if (initialSubtasksGroup) initialSubtasksGroup.classList.add('hidden');
    } else {
        modalTitle.textContent = 'New Project';
        taskIdInput.value = '';
        taskPriorityInput.value = 'Medium';
        taskStatusInput.value = 'To Do';
        taskCategoryInput.value = 'Development';
        taskDueDateInput.value = new Date().toISOString().split('T')[0];
        if (initialSubtasksGroup) initialSubtasksGroup.classList.remove('hidden');
    }
    taskModal.classList.remove('hidden');
    taskTitleInput.focus();
}

function closeModal() {
    taskModal.classList.add('hidden');
}

function editTask(id) {
    SoundEngine.playClick();
    const task = allTasks.find(t => t.id === id);
    if (task) openModal(task);
}

// Submit Project Form
async function handleFormSubmit(e) {
    e.preventDefault();
    SoundEngine.playClick();

    const id = taskIdInput.value ? parseInt(taskIdInput.value) : null;
    const taskData = {
        title: taskTitleInput.value.trim(),
        category: taskCategoryInput.value,
        priority: taskPriorityInput.value,
        status: taskStatusInput.value,
        due_date: taskDueDateInput.value || null,
        description: taskDescriptionInput.value.trim()
    };

    if (!taskData.title) {
        showToast('Title is required', 'error');
        return;
    }

    // Parse initial subtasks if creating
    if (!id && taskInitialSubtasks && taskInitialSubtasks.value.trim()) {
        const lines = taskInitialSubtasks.value.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        taskData.subtasks = lines;
    }

    try {
        let res;
        if (id) {
            res = await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        } else {
            res = await fetch(`/api/tasks?user_id=${currentUser.id || 1}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        }

        if (res.ok) {
            closeModal();
            showToast(id ? 'Project updated!' : 'Project created with subtasks!', 'success');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Delete Logic
function openDeleteModal(id) {
    SoundEngine.playClick();
    taskToDeleteId = id;
    deleteModal.classList.remove('hidden');
}

function closeDeleteModal() {
    taskToDeleteId = null;
    deleteModal.classList.add('hidden');
}

async function confirmDelete() {
    if (!taskToDeleteId) return;
    SoundEngine.playClick();

    try {
        const res = await fetch(`/api/tasks/${taskToDeleteId}`, { method: 'DELETE' });
        if (res.ok) {
            closeDeleteModal();
            showToast('Project and all subtasks deleted', 'info');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Reset Demo Data
async function resetDemoData() {
    SoundEngine.playClick();
    try {
        const res = await fetch('/api/reset-demo', { method: 'POST' });
        if (res.ok) {
            showToast('Demo projects and subtasks restored!', 'info');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ==================== AI ASSISTANT PROJECT BREAKDOWN ====================
function openAIModal() {
    SoundEngine.playClick();
    aiModal.classList.remove('hidden');
    aiResultsContainer.classList.add('hidden');
    aiLoading.classList.add('hidden');
    aiProjectInput.focus();
}

function closeAIModal() {
    aiModal.classList.add('hidden');
}

async function handleAIGenerate() {
    const project = aiProjectInput.value.trim();
    if (!project) {
        showToast('Please enter your project or goal name', 'error');
        return;
    }

    SoundEngine.playClick();
    aiLoading.classList.remove('hidden');
    aiResultsContainer.classList.add('hidden');

    const horizon = aiHorizonSelect.value;
    const customDays = horizon === 'custom' ? parseInt(aiCustomDaysInput.value) || 30 : null;
    
    let numSteps = null;
    if (aiStepsSelect.value !== 'auto') {
        numSteps = aiStepsSelect.value === 'custom' ? parseInt(aiCustomStepsInput.value) || 5 : parseInt(aiStepsSelect.value);
    }

    try {
        const res = await fetch('/api/ai/breakdown', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_title: project,
                horizon: horizon,
                custom_days: customDays,
                num_steps: numSteps
            })
        });

        if (res.ok) {
            const data = await res.json();
            generatedAITasks = data.tasks;
            renderAITasksPreview(generatedAITasks);
            aiLoading.classList.add('hidden');
            aiResultsContainer.classList.remove('hidden');
            SoundEngine.playAI();
        } else {
            throw new Error('AI generation failed');
        }
    } catch (err) {
        aiLoading.classList.add('hidden');
        showToast('Error generating AI plan', 'error');
    }
}

function renderAITasksPreview(tasks) {
    aiTasksList.innerHTML = '';
    aiTasksCount.textContent = `${tasks.length} subtasks`;

    tasks.forEach((t, i) => {
        const item = document.createElement('div');
        item.className = 'ai-task-item';
        item.innerHTML = `
            <input type="checkbox" id="aiCheck_${i}" checked>
            <div class="ai-task-details">
                <input type="text" value="${escapeHtml(t.title)}" class="ai-input-title" 
                       style="width: 100%; font-weight: 700; padding: 0.35rem 0.5rem; font-size: 0.88rem; border: 1px solid var(--border-color); border-radius: var(--radius-sm);" 
                       oninput="updateAIStepField(${i}, 'title', this.value)" title="Edit subtask title">
                
                <div class="ai-task-edit-inputs">
                    <span class="badge badge-cat">${escapeHtml(t.category)}</span>
                    <select onchange="updateAIStepField(${i}, 'priority', this.value)" style="border-radius: var(--radius-sm);">
                        <option value="High" ${t.priority === 'High' ? 'selected' : ''}>High Priority</option>
                        <option value="Medium" ${t.priority === 'Medium' ? 'selected' : ''}>Medium Priority</option>
                        <option value="Low" ${t.priority === 'Low' ? 'selected' : ''}>Low Priority</option>
                    </select>
                    <input type="date" value="${t.due_date}" onchange="updateAIStepField(${i}, 'due_date', this.value)" style="border-radius: var(--radius-sm);">
                    <button type="button" class="btn-ai-remove" onclick="removeAIStep(${i})" title="Remove subtask">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </div>
        `;
        aiTasksList.appendChild(item);
    });
}

function updateAIStepField(index, field, value) {
    if (generatedAITasks[index]) {
        generatedAITasks[index][field] = value;
    }
}

function removeAIStep(index) {
    SoundEngine.playClick();
    generatedAITasks.splice(index, 1);
    renderAITasksPreview(generatedAITasks);
}

function addExtraAIStep() {
    SoundEngine.playClick();
    const today = new Date().toISOString().split('T')[0];
    generatedAITasks.push({
        title: "New Subtask Milestone",
        description: "Milestone added by user",
        category: "Development",
        priority: "Medium",
        status: "To Do",
        due_date: today
    });
    renderAITasksPreview(generatedAITasks);
}

// Import as 1 Big Project with Nested Subtasks
async function handleAIImport() {
    SoundEngine.playClick();

    const selectedSubtasks = [];
    generatedAITasks.forEach((t, i) => {
        const chk = document.getElementById(`aiCheck_${i}`);
        if (chk && chk.checked && t.title.trim()) {
            selectedSubtasks.push(t.title.trim());
        }
    });

    if (selectedSubtasks.length === 0) {
        showToast('Please select at least one subtask', 'error');
        return;
    }

    const projectTitle = aiProjectInput.value.trim() || 'New AI Project';
    const latestDate = generatedAITasks[generatedAITasks.length - 1]?.due_date || new Date().toISOString().split('T')[0];

    const projectPayload = {
        title: projectTitle,
        description: `Project generated by 120B AI Assistant with ${selectedSubtasks.length} milestones.`,
        category: generatedAITasks[0]?.category || 'Development',
        priority: 'High',
        status: 'To Do',
        due_date: latestDate,
        subtasks: selectedSubtasks
    };

    try {
        const res = await fetch(`/api/tasks?user_id=${currentUser.id || 1}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectPayload)
        });

        if (res.ok) {
            closeAIModal();
            SoundEngine.playComplete();
            Confetti.burst();
            showToast(`🚀 "${projectTitle}" created with ${selectedSubtasks.length} subtasks inside!`, 'success');
            loadData();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-circle-exclamation';

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3200);
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}
