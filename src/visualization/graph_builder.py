def map_color_to_status(color):
    if not color:
        return "notbuilt"

    color = color.lower()

    if "blue" in color:
        return "success"
    if "red" in color:
        return "failed"
    if "yellow" in color:
        return "unstable"

    return "notbuilt"


def format_duration(ms):
    if not ms:
        return "-"

    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes}m {seconds}s"


def build_graph(jobs_data):
    nodes = []
    edges = set()

    for job in jobs_data:
        name = job.get("name")

        details = job.get("details", {})

        # ✅ FIX: get color from MAIN job, not details
        status = map_color_to_status(job.get("color"))

        last_build = details.get("lastBuild") or {}

        build_number = last_build.get("number")
        duration = format_duration(last_build.get("duration"))

        upstream_projects = details.get("upstreamProjects") or []
        upstream = [u.get("name") for u in upstream_projects]

        downstream_projects = details.get("downstreamProjects") or []
        downstream = [d.get("name") for d in downstream_projects]

        nodes.append({
            "id": name,
            "label": name,
            "status": status,              # ✅ now correct
            "build_number": build_number,
            "duration": duration,
            "upstream": upstream,
            "downstream": downstream
        })

        for d in downstream:
            edges.add((name, d))

        for u in upstream:
            edges.add((u, name))

    return {
        "nodes": nodes,
        "edges": [{"from": s, "to": t} for s, t in edges]
    }