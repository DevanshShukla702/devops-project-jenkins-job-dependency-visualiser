document.addEventListener('keydown', (e) => {
    // Prevent if inside input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    switch(e.key.toLowerCase()) {
        case 'r':
            if (window.refreshGraph) {
                e.preventDefault();
                refreshGraph();
                showToast("Refreshing Graph...", "success");
            }
            break;
        case 'f':
            if (window.fitGraphView) {
                e.preventDefault();
                fitGraphView();
                showToast("Fitted to view", "success");
            }
            break;
        case 'escape':
            if (window.closeDetailPanel) {
                closeDetailPanel();
            }
            break;
        case '/':
            e.preventDefault();
            const searchBox = document.getElementById('job-search') || document.getElementById('jobs-search-input');
            if(searchBox) searchBox.focus();
            break;
    }
});
