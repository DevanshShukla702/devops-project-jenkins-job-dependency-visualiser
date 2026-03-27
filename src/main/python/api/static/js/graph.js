let network = null;
let allNodes = [];
let allEdges = [];

function getNodeColor(status) {
    const style = getComputedStyle(document.documentElement);
    const get = (v) => style.getPropertyValue(v).trim() || v;
    const map = {
      'success':   { border: get('--node-border-success'), shadow: get('--node-shadow-success') },
      'failed':    { border: get('--node-border-failed'), shadow: get('--node-shadow-failed') },
      'unstable':  { border: get('--node-border-unstable'), shadow: get('--node-shadow-unstable') },
      'not_built': { border: get('--node-border-notbuilt'), shadow: get('--node-shadow-notbuilt') },
      'notbuilt':  { border: get('--node-border-notbuilt'), shadow: get('--node-shadow-notbuilt') }
    };
    return map[status?.toLowerCase()] || map['notbuilt'];
}

function getGraphOptions() {
    const style = getComputedStyle(document.documentElement);
    const get = (v) => style.getPropertyValue(v).trim() || (v.includes('bg') ? '#0B0E14' : '#00F2FF');

    return {
      nodes: {
        shape: 'box',
        borderWidth: 2,
        borderWidthSelected: 3,
        font: {
          face: 'JetBrains Mono, monospace',
          size: 12,
          color: get('--node-text')
        },
        color: {
          background: get('--node-bg'),
          border: get('--node-border-success'),
          highlight: {
            background: get('--node-bg'),
            border: get('--accent-cyan')
          },
          hover: {
            background: get('--node-bg'),
            border: get('--accent-cyan')
          }
        },
        shadow: {
          enabled: true,
          color: get('--node-shadow-success'),
          size: 14,
          x: 0, y: 2
        },
        margin: { top: 8, bottom: 8, left: 14, right: 14 }
      },
      edges: {
        color: {
          color: get('--edge-color'),
          highlight: get('--edge-hover'),
          hover: get('--edge-hover')
        },
        width: 1.5,
        arrows: { to: { enabled: true, scaleFactor: 0.7 } },
        smooth: {
          type: 'cubicBezier',
          forceDirection: 'vertical',
          roundness: 0.4
        }
      },
      physics: { enabled: false },
      layout: {
        hierarchical: {
          direction: 'UD',
          sortMethod: 'directed',
          levelSeparation: 110,
          nodeSpacing: 150
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        zoomView: true,
        dragView: true
      },
      background: { color: 'transparent' }
    };
}

function initGraph(containerId, nodesData, edgesData) {
    const container = document.getElementById(containerId);
    
    const style = getComputedStyle(document.documentElement);
    const get = (v) => style.getPropertyValue(v).trim() || '#0B0E14';
    
    // Configure nodes for UI spec
    const nodes = new vis.DataSet(nodesData.map(n => {
        const c = getNodeColor(n.status || n.color);
        
        let labelStr = n.label;
        if(n.build_number) {
            labelStr += `\n#${n.build_number}`;
        }

        return {
            id: n.id,
            label: labelStr,
            color: {
                background: get('--node-bg'),
                border: c.border,
                highlight: { background: get('--node-bg'), border: get('--accent-cyan') },
                hover: { background: get('--node-bg'), border: get('--accent-cyan') }
            },
            shadow: { color: c.shadow },
            _orig_border: c.border,
            // Metadata for detail panel
            ...n
        };
    }));

    const edges = new vis.DataSet(edgesData.map(e => {
        return {
            ...e,
            arrows: { to: { enabled: true, scaleFactor: 0.65, type: 'arrow' } }
        };
    }));

    const data = { nodes, edges };
    const options = getGraphOptions();

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
        if(window.fitGraphView) window.fitGraphView();
    });
}

function loadGraph(silent = false) {
    if(!silent) {
        const loader = document.getElementById('loader-overlay');
        if(loader) loader.style.display = 'flex';
    }

    fetch('/api/graph')
        .then(response => {
            if (!response.ok) return response.json().then(j => { throw new Error(j.error || "HTTP Error"); });
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
            if(loader) loader.innerHTML = `<p style="color:var(--accent-red)">Error connected to backend: ${err.message}</p>`;
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
}

window.highlightNode = function(nodeId) {
    if(!network) return;
    network.selectNodes([nodeId]);
    network.focus(nodeId, {
        scale: 1.2,
        animation: { duration: 500, easingFunction: "easeOutCubic" }
    });
};

window.traceNodePath = function(nodeId) {
    if(!network || !network.body.data.nodes) return;
    
    const btn = document.querySelector('.detail-body .btn-primary');
    if (btn && btn.innerText === "Reset Trace") {
        if(window.resetTrace) window.resetTrace();
        return;
    }
    
    let connectedNodes = new Set();
    connectedNodes.add(nodeId);
    
    function getUp(id) {
        const edges = network.getConnectedEdges(id);
        edges.forEach(eId => {
            const edge = network.body.data.edges.get(eId);
            if(edge && edge.to === id && !connectedNodes.has(edge.from)) {
                connectedNodes.add(edge.from);
                getUp(edge.from);
            }
        });
    }
    
    function getDown(id) {
        const edges = network.getConnectedEdges(id);
        edges.forEach(eId => {
            const edge = network.body.data.edges.get(eId);
            if(edge && edge.from === id && !connectedNodes.has(edge.to)) {
                connectedNodes.add(edge.to);
                getDown(edge.to);
            }
        });
    }
    
    getUp(nodeId);
    getDown(nodeId);
    
    const allNs = network.body.data.nodes.get();
    const style = getComputedStyle(document.documentElement);
    const get = (v) => style.getPropertyValue(v).trim() || '#0B0E14';
    
    const updatesN = allNs.map(n => ({
        id: n.id,
        color: connectedNodes.has(n.id) 
            ? { background: get('--node-bg'), border: n._orig_border, highlight: { background: get('--node-bg'), border: get('--accent-cyan') }, hover: { background: get('--node-bg'), border: get('--accent-cyan') } } 
            : { background: get('--bg-app'), border: 'rgba(50,50,50,0.4)', highlight: { background: get('--bg-app'), border: 'rgba(50,50,50,0.4)' }, hover: { background: get('--bg-app'), border: 'rgba(50,50,50,0.4)' } },
        font: connectedNodes.has(n.id) ? { color: get('--node-text') } : { color: 'rgba(100,100,100,0.4)' }
    }));
    network.body.data.nodes.update(updatesN);
    
    const allEs = network.body.data.edges.get();
    const updatesE = allEs.map(e => ({
        id: e.id,
        color: (connectedNodes.has(e.from) && connectedNodes.has(e.to)) ? null : { color: 'rgba(50,50,50,0.1)' }
    }));
    network.body.data.edges.update(updatesE);
    
    network.fit({
        nodes: Array.from(connectedNodes),
        animation: { duration: 800, easingFunction: "easeInOutQuad" }
    });

    if (btn) btn.innerText = "Reset Trace";
    if(window.showToast) window.showToast(`Full recursive trace isolated`, 'success');
};

window.resetTrace = function() {
    if(!network || !network.body.data.nodes) return;
    
    const allNs = network.body.data.nodes.get();
    const style = getComputedStyle(document.documentElement);
    const get = (v) => style.getPropertyValue(v).trim() || '#0B0E14';
    
    const updatesN = allNs.map(n => ({
        id: n.id,
        color: { background: get('--node-bg'), border: n._orig_border, highlight: { background: get('--node-bg'), border: get('--accent-cyan') }, hover: { background: get('--node-bg'), border: get('--accent-cyan') } },
        font: { color: get('--node-text') }
    }));
    network.body.data.nodes.update(updatesN);
    
    const allEs = network.body.data.edges.get();
    const updatesE = allEs.map(e => ({ id: e.id, color: null }));
    network.body.data.edges.update(updatesE);
    
    const btn = document.querySelector('.detail-body .btn-primary');
    if (btn) btn.innerText = "Trace Path";
    
    network.fit({ animation: { duration: 800, easingFunction: "easeInOutQuad" } });
};

document.addEventListener("DOMContentLoaded", () => {
    loadGraph();
});
