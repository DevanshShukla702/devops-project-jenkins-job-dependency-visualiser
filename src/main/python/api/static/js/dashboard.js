let statsRefreshInterval = null;
let graphRefreshInterval = null;
let autoRefreshEnabled = false;

// Format duration utility
function formatDuration(ms) {
    if(!ms) return '-';
    let s = Math.floor(ms / 1000);
    let m = Math.floor(s / 60);
    s = s % 60;
    return `${m}m ${s}s`;
}

// Stats loading
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        
        document.getElementById('stat-total').innerText = data.total_jobs;
        
        // Handle no jobs division by zero case
        const rate = data.total_jobs > 0 ? Math.round((data.success_count / data.total_jobs) * 100) : 0;
        document.getElementById('stat-success-rate').innerText = `${rate}%`;
        document.getElementById('stat-failed').innerText = data.failed_count;
        
        updateLastRefreshed();
    } catch(err) {
        console.error("Failed to load stats", err);
    }
}

// Side-bar specific Jobs loading
async function loadSidebarJobs() {
    try {
        const res = await fetch('/api/jobs');
        const jobs = await res.json();
        
        // Store globally for filtering
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
        let status = job.color.replace('_anime','').replace('anime','').replace('blue', 'success').replace('red', 'failed').replace('yellow', 'unstable');
        if(!['success','failed','unstable'].includes(status)) status = 'notbuilt';

        if(filter !== 'all' && status !== filter) return;
        if(query && !job.name.toLowerCase().includes(query)) return;
        
        const div = document.createElement('div');
        div.className = 'job-item';
        div.onclick = () => {
            if(window.highlightNode) window.highlightNode(job.name);
            openDetailPanel(job.name);
        };
        
        div.innerHTML = `
            <div class="job-dot ${status}"></div>
            <div class="mono" style="font-size: 0.9rem">${job.name}</div>
        `;
        list.appendChild(div);
    });
}

// Detail panel logic
function openDetailPanel(nodeId) {
    const panel = document.getElementById('detail-panel');
    panel.classList.add('open');
    
    if(!window.allGraphNodes) return;
    const nodeData = window.allGraphNodes.find(n => n.id === nodeId);
    if(!nodeData) return;
    
    document.getElementById('dp-title').innerText = nodeData.label;
    
    const dpStatus = document.getElementById('dp-status');
    dpStatus.className = `status-pill status-${nodeData.status}`;
    dpStatus.innerText = nodeData.status;

    document.getElementById('dp-build').innerText = nodeData.build_number ? `#${nodeData.build_number}` : '-';
    document.getElementById('dp-duration').innerText = nodeData.duration || '-';
    
    const renderChips = (arr) => arr.length ? arr.map(e => `<span class="chip" onclick="openDetailPanel('${e}'); if(window.highlightNode) window.highlightNode('${e}')">${e}</span>`).join('') : '-';
    
    document.getElementById('dp-upstream').innerHTML = renderChips(nodeData.upstream || []);
    document.getElementById('dp-downstream').innerHTML = renderChips(nodeData.downstream || []);
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('open');
    if(window.network) window.network.unselectAll();
}

function tracePath() {
    const nodeId = document.getElementById('dp-title').innerText;
    if(window.traceNodePath) {
        window.traceNodePath(nodeId);
        showToast(`Tracing path for ${nodeId}`, 'success');
    }
}

function openJenkins() {
    const nodeId = document.getElementById('dp-title').innerText;
    window.open(`http://localhost:8080/job/${encodeURIComponent(nodeId)}`, '_blank');
}

// Auto refresh
function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const btn = document.getElementById('auto-refresh-btn');
    if(autoRefreshEnabled) {
        btn.style.background = 'var(--accent-color)';
        btn.style.color = 'var(--bg-color)';
        btn.innerText = '⏱ (On)';
        showToast("Auto-refresh enabled (30s)", "success");
        // Start timers
        graphRefreshInterval = setInterval(() => {
            if(window.refreshGraph) window.refreshGraph(true); // silent refresh
        }, 30000);
    } else {
        btn.style.background = '';
        btn.style.color = '';
        btn.innerText = '⏱';
        showToast("Auto-refresh disabled", "success");
        clearInterval(graphRefreshInterval);
    }
}

function updateLastRefreshed() {
    const d = new Date();
    document.getElementById('stat-last-refreshed').innerText = `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`;
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    loadStats();
    loadSidebarJobs();
    
    // Filters
    let currentFilter = 'all';
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderSidebarJobs(currentFilter, document.getElementById('job-search').value);
        });
    });
    
    // Search
    document.getElementById('job-search').addEventListener('input', (e) => {
        renderSidebarJobs(currentFilter, e.target.value);
    });

    // Auto-refresh btn
    document.getElementById('auto-refresh-btn').addEventListener('click', toggleAutoRefresh);
    
    // Initial highlight logic for redirects from /jobs (e.g., ?highlight=...)
    const urlParams = new URLSearchParams(window.location.search);
    const highlightTarget = urlParams.get('highlight');
    if(highlightTarget) {
        // give graph time to render
        setTimeout(() => {
            if(window.highlightNode) window.highlightNode(highlightTarget);
            openDetailPanel(highlightTarget);
        }, 1000);
    }
});
