from flask import Blueprint, render_template, request, jsonify
from core.logging_config import LoggerSetup
from projects.sheet_updater_handler import run_sheet_updater, progress
from core.config_manager import ConfigurationManager
import threading

sheet_updater_bp = Blueprint('sheet_updater', __name__)
logger = LoggerSetup.setup_logger("sheet_updater_ui", "logs/sheet_updater_ui")

sheet_updater_config_path = "configs/sheet_updater.json"

@sheet_updater_bp.route("/sheet-updater", methods=["GET"])
def show_sheet_updater_form():
    """
    Show the sheet updater UI.
    """
    config_mgr = ConfigurationManager(config_file=sheet_updater_config_path)
    sheet_url = config_mgr.get("SHEET_URL", "")
    
    return render_template("sheet_updater.html", sheet_url=sheet_url)


@sheet_updater_bp.route("/sheet-updater/start", methods=["POST"])
def start_sheet_updater():
    """
    Start the sheet updater job.
    """
    try:
        global progress
        
        # Check if already running
        if progress["status"] == "running":
            return jsonify({
                "status": "error", 
                "message": "Sheet updater is already running"
            }), 400
        
        # Get sheet URL from form
        sheet_url = request.form.get("sheet_url", "").strip()
        
        if not sheet_url:
            return jsonify({
                "status": "error",
                "message": "Sheet URL is required"
            }), 400
        
        # Start the job in a separate thread
        thread = threading.Thread(target=run_sheet_updater, args=(sheet_url,))
        thread.start()
        
        logger.info(f"Sheet updater job started for sheet: {sheet_url}")
        
        return jsonify({
            "status": "success",
            "message": "Sheet updater job started successfully"
        })
        
    except Exception as e:
        logger.exception("Error starting sheet updater job")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@sheet_updater_bp.route("/sheet-updater/progress", methods=["GET"])
def get_sheet_updater_progress():
    """
    Get the current progress of the sheet updater job.
    """
    return jsonify(progress)


@sheet_updater_bp.route("/sheet-updater/config", methods=["GET", "POST"])
def manage_sheet_updater_config():
    """
    Manage sheet updater configuration.
    """
    config_mgr = ConfigurationManager(config_file=sheet_updater_config_path)
    
    if request.method == "GET":
        return jsonify(config_mgr.get_project_only())
    
    if request.method == "POST":
        try:
            new_config = request.get_json()
            for key, value in new_config.items():
                config_mgr.set(key, value)
            return jsonify({
                "status": "success",
                "message": "Configuration updated successfully"
            })
        except Exception as e:
            logger.exception("Error updating configuration")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
