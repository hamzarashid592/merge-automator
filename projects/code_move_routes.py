from flask import Blueprint, render_template, request, jsonify
from core.logging_config import LoggerSetup
from projects.code_move_handler import clone_mantis_tickets
from core.config_manager import ConfigurationManager

code_move_bp = Blueprint('code_move', __name__)
logger = LoggerSetup.setup_logger("code_move_ui", "logs/code_move_ui")

code_move_config_path = "configs/code_move.json"

@code_move_bp.route("/code-move", methods=["GET"])
def show_code_move_form():
    return render_template("code_move.html")

@code_move_bp.route("/code-move/start", methods=["POST"])
def start_code_move():
    try:
        ticket_ids = request.form.get("ticket_ids", "")
        er_date = request.form.get("er_date", "")
        target_version = request.form.get("target_version", "")
        target_patch = request.form.get("target_patch", "")
        qa_owner = request.form.get("qa_owner", "")
        title_prefix = request.form.get("title_prefix", "")
        instructions = request.form.get("instructions", "")

        ticket_ids = [t.strip() for t in ticket_ids.split(",") if t.strip()]

        result = clone_mantis_tickets(
            ticket_ids=ticket_ids,
            er_date=er_date,
            target_version=target_version,
            target_patch=target_patch,
            qa_owner=qa_owner,
            instructions=instructions,
            title_prefix = title_prefix
        )

        return render_template("code_move.html", status=result["status"], percentage=result["percentage"], error=result.get("error", ""))
    except Exception as e:
        logger.exception("Error starting code move job")
        return render_template("code_move.html", status="error", percentage=0, error=str(e))


@code_move_bp.route("/code-move/progress", methods=["GET"])
def get_code_move_progress():
    from projects.code_move_handler import progress
    return jsonify(progress)


@code_move_bp.route("/code-move/config", methods=["GET"])
def show_code_move_config_page():
    return render_template("code_move_config.html")

@code_move_bp.route("/code-move/config/data", methods=["GET", "POST"])
def handle_code_move_config():
    config_mgr = ConfigurationManager(config_file="configs/code_move.json")

    if request.method == "GET":
        common_config, project_config = config_mgr.get_sources()
        return jsonify({
            "common": common_config,
            "project": project_config
        })

    if request.method == "POST":
        try:
            new_config = request.get_json()
            for key, value in new_config.items():
                config_mgr.set(key, value)
            return jsonify({"status": "success", "message": "Configuration updated."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

        

@code_move_bp.route("/code-move/options", methods=["GET"])
def get_dropdown_options():
    config_mgr = ConfigurationManager(config_file="configs/code_move.json")
    return jsonify({
        "qa_owners": config_mgr.get("QA_OWNERS", []),
        "target_versions": config_mgr.get("TARGET_VERSIONS", []),
        "target_patches": config_mgr.get("TARGET_PATCHES", [])
    })
