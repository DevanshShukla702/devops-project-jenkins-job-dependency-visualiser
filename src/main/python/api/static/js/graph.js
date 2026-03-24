let network = null;
let allNodes = [];
let allEdges = [];

const colorMap = {
    'success': { border: '#00ff88', background: '#092b28', highlight: '#00ff88' },
    'failed': { border: '#ff4444', background: '#2e0c16', highlight: '#ff4444' },
    'unstable': { border: '#ffb800', background: '#2e2416', highlight: '#ffb800' },
    'notbuilt': { border: '#64748b', background: '#171c28', highlight: '#94a3b8' }
};

function initGraph(containerId, nodesData, edgesData) {
    const container = document.getElementById(containerId);
    
    // Configure nodes for UI spec
    const nodes = new vis.DataSet(nodesData.map(n => {
        const c = colorMap[n.status] || colorMap['notbuilt'];
        
        let labelStr = n.label;
        if(n.build_number) {
            labelStr += `\n#${n.build_number}`;
        }

        return {
            id: n.id,
            label: labelStr,
            shape: 'box',
            margin: { top: 12, right: 20, bottom: 12, left: 20 },
            color: {
                border: c.border,
                background: c.background,
                highlight: {
                    border: c.highlight,
                    background: c.background
                },
                hover: {
                    border: c.highlight,
                    background: c.background
                }
            },
            font: {
                color: '#ffffff',
                face: 'Inter, sans-serif',
                size: 14,
                multi: true
            },
            borderWidth: 2,
            borderWidthSelected: 4,
            shadow: {
                enabled: true,
                color: c.border.replace('rgb', 'rgba').replace(')', ', 0.3)'),
                size: 20,
                x: 0,
                y: 0
            },
            // Metadata for detail panel
            ...n
        };
    }));

    const edges = new vis.DataSet(edgesData.map(e => ({
        ...e,
        color: { color: 'rgba(255, 255, 255, 0.4)', highlight: '#00f5ff' },
        width: 2,
        hoverWidth: 3,
        selectionWidth: 4,
        arrows: { to: { enabled: true, scaleFactor: 0.7 } },
        smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.6 }
    })));

    const data = { nodes, edges };
    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'UD',
                sortMethod: 'directed',
                nodeSpacing: 250,
                levelSeparation: 150,
                treeSpacing: 200,
                blockShifting: true,
                edgeMinimization: true,
                parentCentralization: true,
            }
        },
        physics: false,
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragView: true
        }
    };

    network = new vis.Network(container, data, options);
    window.network = network;
    window.allGraphNodes = nodesData;
    
    // Hide loader
    const loader = document.getElementById('loader-overlay');
    if(loader) loader.style.display = 'none';

    // Events
    network.on("selectNode", function (params) {
        if(params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            if(window.openDetailPanel) window.openDetailPanel(nodeId);
        }
    });

    network.on("deselectNode", function (params) {
        if(window.closeDetailPanel) window.closeDetailPanel();
    });
    
    // Fit View after stabilisation
    network.once("afterDrawing", function() {
        network.fit({
            animation: {
                duration: 1000,
                easingFunction: "easeInOutQuad"
            }
        });
    });
}

function loadGraph(silent = false) {
    if(!silent) {
        const loader = document.getElementById('loader-overlay');
        if(loader) loader.style.display = 'flex';
    }

    fetch('/api/graph')
        .then(response => {
            if (!response.ok) {
                 return response.json().then(json => { throw new Error(json.error || `HTTP ${response.status}`); });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) throw new Error(data.error);
            initGraph('network', data.nodes, data.edges);
            if(window.loadStats) window.loadStats();
        })
        .catch(err => {
            console.error("Error loading graph:", err);
            const loader = document.getElementById('loader-overlay');
            if(loader) loader.innerHTML = `<p style="color:var(--danger-color)">Error connecting to backend.</p>`;
        });
}

window.refreshGraph = function(silent = false) {
    loadGraph(silent);
};

window.fitGraphView = function() {
    if(network) {
        network.fit({ animation: { duration: 500, easingFunction: "easeOutQuad" } });
    }
};

window.exportGraph = function() {
    if(!network) return;
    const canvas = document.querySelector("#network canvas");
    if(!canvas) return;
    
    const link = document.createElement("a");
    link.href = canvas.toDataURL("image/png");
    link.download = "flowtrace-graph.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    if(window.showToast) window.showToast("Graph exported as PNG", "success");
};

window.highlightNode = function(nodeId) {
    if(!network) return;
    network.selectNodes([nodeId]);
    network.focus(nodeId, {
        scale: 1.2,
        animation: { duration: 500, easingFunction: "easeOutCubic" }
    });
};

document.addEventListener("DOMContentLoaded", () => {
    loadGraph();
});
