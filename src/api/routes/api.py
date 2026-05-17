import logging
from flask import Blueprint, jsonify
from api.utils import get_service, require_auth
from visualization.graph_builder import build_graph

logger = logging.getLogger("flowtrace")
api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/health")
def health_check():
    """Lightweight health check -- no DB dependency."""
    return jsonify({"status": "ok", "app": "FlowTrace"}), 200

@api_bp.route("/graph")
@require_auth
def graph():
    try:
        service = get_service()
        jobs = service.get_all_jobs()
        jobs_data = []

        for job in jobs:
            name = job["name"]
            details = service.get_job_details(name)
            jobs_data.append(
                {
                    "name": name,
                    "color": job.get("color", "notbuilt"),
                    "details": details,
                }
            )

        return jsonify(build_graph(jobs_data))
    except Exception as e:
        logger.error(f"Graph API error: {e}", exc_info=True)
        return jsonify({"error": "Failed to load graph data"}), 500

@api_bp.route("/jobs")
@require_auth
def api_jobs():
    try:
        service = get_service()
        jobs = service.get_all_jobs()

        jobs_detail_list = []
        for job in jobs:
            name = job["name"]
            details = service.get_job_details(name)
            last_build = details.get("lastBuild", {}) or {}

            upstream_projects = details.get("upstreamProjects") or []
            downstream_projects = details.get("downstreamProjects") or []

            jobs_detail_list.append(
                {
                    "name": name,
                    "color": job.get("color", "notbuilt"),
                    "build_number": last_build.get("number"),
                    "duration": last_build.get("duration"),
                    "upstream": [u.get("name") for u in upstream_projects],
                    "downstream": [d.get("name") for d in downstream_projects],
                }
            )

        return jsonify(jobs_detail_list)
    except Exception as e:
        logger.error(f"Jobs API error: {e}", exc_info=True)
        return jsonify({"error": "Failed to load jobs data"}), 500

@api_bp.route("/stats")
@require_auth
def api_stats():
    try:
        service = get_service()
        jobs = service.get_all_jobs()

        success_count = sum(1 for j in jobs if j.get("color", "").startswith("blue"))
        failed_count = sum(1 for j in jobs if j.get("color", "").startswith("red"))
        unstable_count = sum(1 for j in jobs if j.get("color", "").startswith("yellow"))

        return jsonify(
            {
                "total_jobs": len(jobs),
                "success_count": success_count,
                "failed_count": failed_count,
                "unstable_count": unstable_count,
                "last_updated": "Just now",
            }
        )
    except Exception as e:
        logger.error(f"Stats API error: {e}", exc_info=True)
        return jsonify({"error": "Failed to load stats"}), 500
