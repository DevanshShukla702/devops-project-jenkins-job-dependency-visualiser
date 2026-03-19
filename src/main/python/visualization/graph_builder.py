def build_graph(jobs_data):
    nodes = []
    edges = set()

    for job in jobs_data:
        name = job["name"]
        details = job["details"]

        status = details.get("color", "notbuilt").upper()

        last_build = details.get("lastBuild")
        build_number = last_build.get("number") if last_build else None

        upstream = [u["name"] for u in details.get("upstreamProjects", [])]
        downstream = [d["name"] for d in details.get("downstreamProjects", [])]

        nodes.append({
            "id": name,
            "label": name,
            "status": status,
            "build": build_number,
            "upstream": upstream,
            "downstream": downstream
        })

        for d in downstream:
            edges.add((name, d))

        for u in upstream:
            edges.add((u, name))

    return {
        "nodes": nodes,
        "edges": [{"source": s, "target": t} for s, t in edges]
    }