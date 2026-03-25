// Utilities
function formatDuration(ms) {
    if(!ms) return '-';
    let s = Math.floor(ms / 1000);
    let m = Math.floor(s / 60);
    s = s % 60;
    return `${m}m ${s}s`;
}

function countUp(el, target, isPercentage = false, duration = 800) {
    const start = performance.now();
    const update = (now) => {
        const t = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - t, 3);
        const val = Math.round(ease * target);
        el.textContent = val + (isPercentage ? '%' : '');
        if (t < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
}

// Stats logic
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        
        // Hide skeletons, show metrics
        ['total', 'success-rate', 'failed', 'refreshed'].forEach(id => {
            const skel = document.getElementById(`stat-${id}-skeleton`);
            if (skel) skel.style.display = 'none';
        });

        const elTotal = document.getElementById('stat-total');
        elTotal.style.display = 'inline';
        countUp(elTotal, data.total_jobs);

        const rate = data.total_jobs > 0 ? Math.round((data.success_count / data.total_jobs) * 100) : 0;
        const elRate = document.getElementById('stat-success-rate');
        elRate.style.display = 'inline';
        countUp(elRate, rate, true);

        const elFailed = document.getElementById('stat-failed');
        elFailed.style.display = 'inline';
        countUp(elFailed, data.failed_count);
        
        updateLastRefreshed();
    } catch(err) {
        console.error("Failed to load stats", err);
    }
}

// Sidebar jobs logic
async function loadSidebarJobs() {
    try {
        const res = await fetch('/api/jobs');
        const jobs = await res.json();
        
        window.allJobsData = jobs;
        renderSidebarJobs();
    } catch(err) {
        console.error("Failed to load sidebar jobs", err);
    }
}

function renderSidebarJobs(filter = 'all', searchQuery = '') {
    const list = document.getElementById('jobs-list');
    list.innerHTML = '';
    
    if(!window.allJobsData) return;
    
    const query = searchQuery.toLowerCase();
    
    window.allJobsData.forEach(job => {
        let status = job.color ? job.color.replace('_anime','').replace('anime','').replace('blue', 'success').replace('red', 'failed').replace('yellow', 'unstable') : 'notbuilt';
        if(!['success','failed','unstable'].includes(status)) status = 'notbuilt';

        if(filter !== 'all' && status !== filter) return;
        if(query && !job.name.toLowerCase().includes(query)) return;
        
        const div = document.createElement('div');
        div.className = 'job-item';
        div.onclick = () => {
            // Unselect others
            document.querySelectorAll('.job-item').forEach(el => el.classList.remove('active'));
            div.classList.add('active');
            if(window.highlightNode) window.highlightNode(job.name);
            openDetailPanel(job.name);
        };
        
        div.innerHTML = `
            <div class="job-dot ${status}"></div>
            <div class="job-name">${job.name}</div>
            <div class="job-build">${job.lastBuild ? '#' + job.lastBuild.number : '-'}</div>
        `;
        list.appendChild(div);
    });
}

function openDetailPanel(nodeId) {
    const panel = document.getElementById('detail-panel');
    panel.classList.add('open');
    
    if(!window.allGraphNodes) return;
    const nodeData = window.allGraphNodes.find(n => n.id === nodeId);
    if(!nodeData) return;
    
    document.getElementById('dp-title').innerText = nodeData.label.split('\n')[0];
    
    const dpStatus = document.getElementById('dp-status');
    dpStatus.className = `status-pill status-${nodeData.status.toLowerCase()}`;
    dpStatus.innerText = nodeData.status.toUpperCase();

    document.getElementById('dp-build').innerText = nodeData.build_number ? `#${nodeData.build_number}` : '-';
    document.getElementById('dp-duration').innerText = nodeData.duration || '-';
    
    const renderChips = (arr) => arr.length ? arr.map(e => `<span class="chip" onclick="openDetailPanel('${e}'); if(window.highlightNode) window.highlightNode('${e}')">${e}</span>`).join('') : '-';
    
    document.getElementById('dp-upstream').innerHTML = renderChips(nodeData.upstream || []);
    document.getElementById('dp-downstream').innerHTML = renderChips(nodeData.downstream || []);
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('open');
    if(window.network) window.network.unselectAll();
    document.querySelectorAll('.job-item').forEach(el => el.classList.remove('active'));
}

function tracePath() {
    const nodeId = document.getElementById('dp-title').innerText;
    if(window.traceNodePath) {
        window.traceNodePath(nodeId);
        if(window.showToast) window.showToast(`Tracing path for ${nodeId}`, 'success');
    }
}

function openJenkins() {
    const nodeId = document.getElementById('dp-title').innerText;
    window.open(`http://localhost:8080/job/${encodeURIComponent(nodeId)}`, '_blank');
}

function updateLastRefreshed() {
    const d = new Date();
    const timeStr = `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`;
    document.getElementById('stat-last-refreshed').innerHTML = timeStr;
}

let autoRefreshEnabled = false;
let graphRefreshInterval = null;

function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const btn = document.getElementById('auto-refresh-btn');
    if(autoRefreshEnabled) {
        btn.style.background = 'var(--accent-cyan)';
        btn.style.color = 'var(--bg-app)';
        btn.innerText = '⏱ (On)';
        if(window.showToast) window.showToast("Auto-refresh enabled (30s)", "success");
        // Start timers
        graphRefreshInterval = setInterval(() => {
            if(window.refreshGraph) window.refreshGraph(true); // silent refresh
        }, 30000);
    } else {
        btn.style.background = '';
        btn.style.color = '';
        btn.innerText = '⏱';
        if(window.showToast) window.showToast("Auto-refresh disabled", "success");
        clearInterval(graphRefreshInterval);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Initial fetch
    loadStats();
    loadSidebarJobs();
    
    const autoRefreshBtn = document.getElementById('auto-refresh-btn');
    if (autoRefreshBtn) {
        autoRefreshBtn.addEventListener('click', toggleAutoRefresh);
    }
    
    // Filters logic
    let currentFilter = 'all';
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderSidebarJobs(currentFilter, document.getElementById('job-search').value);
        });
    });
    
    // Search logic
    const searchInput = document.getElementById('job-search');
    if(searchInput) {
        searchInput.addEventListener('input', (e) => {
            renderSidebarJobs(currentFilter, e.target.value);
        });
    }
    
    // Pre-highlight logic
    const urlParams = new URLSearchParams(window.location.search);
    const highlightTarget = urlParams.get('highlight');
    if(highlightTarget) {
        setTimeout(() => {
            if(window.highlightNode) window.highlightNode(highlightTarget);
            openDetailPanel(highlightTarget);
        }, 1500);
    }
});
