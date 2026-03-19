let network = null;
let graphDataGlobal = null;

function getColor(status) {
    if (status.includes("BLUE") || status.includes("SUCCESS"))
        return { background: "#16a34a", border: "#15803d" };
    if (status.includes("FAIL"))
        return { background: "#dc2626", border: "#b91c1c" };
    if (status.includes("UNSTABLE"))
        return { background: "#f59e0b", border: "#d97706" };

    return { background: "#374151", border: "#1f2937" };
}

async function loadGraph() {
    const res = await fetch("/api/graph");
    const data = await res.json();

    graphDataGlobal = data;

    const nodes = new vis.DataSet(
        data.nodes.map(n => ({
            id: n.id,
            label: `${n.id}\n#${n.build || "-"}`,
            shape: "box",
            margin: 10,
            font: { color: "#fff" },
            color: getColor(n.status)
        }))
    );

    const edges = new vis.DataSet(
        data.edges.map((e, i) => ({
            id: i,
            from: e.source,
            to: e.target,
            arrows: "to"
        }))
    );

    const container = document.getElementById("network");

    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: "LR",
                sortMethod: "directed"
            }
        },
        physics: false
    };

    network = new vis.Network(container, { nodes, edges }, options);

    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            showDetails(params.nodes[0]);
        }
    });
}

function showDetails(jobId) {
    const job = graphDataGlobal.nodes.find(n => n.id === jobId);

    document.getElementById("details").innerHTML = `
        <h2>${job.id}</h2>
        <p>Status: ${job.status}</p>
        <p>Build: ${job.build || "-"}</p>
        <p>Upstream: ${job.upstream.join(", ") || "None"}</p>
        <p>Downstream: ${job.downstream.join(", ") || "None"}</p>
    `;
}

window.loadGraph = loadGraph;