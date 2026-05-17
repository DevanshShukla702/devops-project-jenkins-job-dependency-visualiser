let network = null;
let graphDataGlobal = null;

const STATUS_COLORS = {
    success: "#22c55e",
    unstable: "#f59e0b",
    failed: "#ef4444",
    notbuilt: "#64748b"
};

function buildNode(node) {
    const color = STATUS_COLORS[node.status] || "#64748b";

    return {
        id: node.id,
        label: `${node.id}\n#${node.build_number || "-"}`,
        shape: "box",

        margin: { top:12, bottom:12, left:16, right:16 },

        font: {
            color: "#f8fafc",
            size: 13,
            face: "JetBrains Mono",
            multi: true
        },

        color: {
            background: "#1e293b",
            border: color,
            highlight: {
                background: "#263550",
                border: "#3b82f6"
            }
        },

        borderWidth: 2,
        borderWidthSelected: 3,

        shadow: {
            enabled: true,
            color: color,
            size: 12
        },
        widthConstraint: {
            minimum: 140,
            maximum: 180
        }
    };
}

function showDetails(jobId) {
    const job = graphDataGlobal.nodes.find(n => n.id === jobId);
    if (!job) return;

    document.getElementById("job-title").innerText = job.id;

    document.getElementById("job-details").innerHTML = `
        <div class="badge ${job.status}">${job.status.toUpperCase()}</div>

        <div class="info-row">
            <span>Build</span>
            <span>#${job.build_number || "-"}</span>
        </div>

        <div class="info-row">
            <span>Upstream</span>
            <span>${job.upstream.length ? job.upstream.join(", ") : "None"}</span>
        </div>

        <div class="info-row">
            <span>Downstream</span>
            <span>${job.downstream.length ? job.downstream.join(", ") : "None"}</span>
        </div>
    `;
}

async function loadGraph() {
    const res = await fetch("/api/graph");
    const data = await res.json();

    graphDataGlobal = data;

    const nodes = new vis.DataSet(
        data.nodes.map(n => buildNode(n))
    );

    const edges = new vis.DataSet(
        data.edges.map((e, i) => ({
            id: i,
            from: e.from,
            to: e.to,

            arrows: { to: { enabled: true } },

            color: {
                color: "#3b82f6",
                highlight: "#60a5fa"
            },

            width: 2,

            smooth: {
                type: "cubicBezier",
                forceDirection: "vertical",
                roundness: 0.5
            },

            shadow: {
                enabled: true,
                color: "rgba(59,130,246,0.4)",
                size: 6
            }
        }))
    );

    const container = document.getElementById("network");

    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: "UD",
                sortMethod: "directed",

                levelSeparation: 180,   // ⬆ more vertical gap
                nodeSpacing: 180,       // ⬆ more horizontal spacing
                treeSpacing: 200,       // ⬆ spacing between branches

                blockShifting: true,
                edgeMinimization: true,
                parentCentralization: true
            }
        },
        physics: {
            enabled: true,
            hierarchicalRepulsion: {
                nodeDistance: 180,
                avoidOverlap: 1
            },
            solver: "hierarchicalRepulsion"
        },
        interaction: { hover: true }
    };

    if (network) network.destroy();

    network = new vis.Network(container, { nodes, edges }, options);

    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            showDetails(params.nodes[0]);
        }
    });

    network.on("hoverNode", () => {
        document.body.style.cursor = "pointer";
    });

    network.on("blurNode", () => {
        document.body.style.cursor = "default";
    });

    setTimeout(() => {
        network.fit({
            animation: {
                duration: 600,
                easingFunction: "easeInOutQuad"
            },
            padding: {
                top: 50,
                bottom: 50,
                left: 50,
                right: 50
            }
        });
    }, 300);
}

window.loadGraph = loadGraph;