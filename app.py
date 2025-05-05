from flask import Flask, render_template, send_file, abort, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
import threading
from projects.merger.factory import MergerFactory
import os
from projects.code_move_routes import code_move_bp 
from core.config_manager import ConfigurationManager
from core.string_constants import StringConstants
from encryption.token_manager import TokenManager
from notifier.chat_notifier import ChatNotifier
from core.string_constants import StringConstants

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

app.register_blueprint(code_move_bp)

# Store active merger instances by ticket type
active_mergers = {}


# Paths to log directories
LOGS_DIRECTORY = "logs"
CONFIG_FILE = "configs/common.json"


@app.route("/")
def home():
    """
    Home page displaying options to trigger the job and view logs.
    """
    ticket_types = {
        "regression": StringConstants.REGRESSION,
        "ps": StringConstants.PROD_SUPPORT
    }
    return render_template("index.html", ticket_types=ticket_types)


# Load configuration
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

# Save configuration
def save_config(new_config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(new_config, file, indent=4)

config = load_config()

# Function to run the merge automation
def run_merge_automation(ticket_type):
    try:
        merger = MergerFactory.get_merger(ticket_type)
        active_mergers[ticket_type] = merger
        merger.run()
        print(f"{ticket_type.title()} job executed successfully at {datetime.now()}")

        notifier = ChatNotifier(
            ticket_type=ticket_type,
            log_dir="logs"
        )
        notifier.send_summary()


    except Exception as e:
        print(f"Error executing {ticket_type} job: {e}")


# # Function to update the job schedule
# def update_scheduler():
#     """
#     Update the scheduler based on the configured time.
#     """
#     time_config = config.get("EXECUTION_TIME", "22:00")  # Default to 10:00 PM
#     hour, minute = map(int, time_config.split(":"))

#     # Remove existing job if it exists
#     scheduler.remove_all_jobs()

#     # Add the new job
#     scheduler.add_job(run_merge_automation, CronTrigger(hour=hour, minute=minute))
#     print(f"Job scheduled daily at {time_config}")

# # Initialize the scheduler
# update_scheduler()


@app.route("/trigger-job/<ticket_type>", methods=["GET", "POST"])
def trigger_job(ticket_type):
    """
    Endpoint to trigger the merge automation job for a specific ticket type.
    """
    merger = active_mergers.get(ticket_type)

    if merger and merger.progress["status"] == "running":
        return jsonify({"status": "error", "message": f"{ticket_type} job is already running."}), 400

    threading.Thread(target=run_merge_automation, args=(ticket_type,)).start()
    return jsonify({"status": "success", "message": f"{ticket_type.title()} job started."})



# Fetch the current progress
@app.route("/progress/<ticket_type>", methods=["GET"])
def get_progress(ticket_type):
    """
    Fetch current progress of the job for a specific ticket type.
    """
    merger = active_mergers.get(ticket_type)

    if not merger:
        return jsonify({"status": "idle", "percentage": 0})  # fallback for first-time view

    return jsonify(merger.progress)





# Config related endpoints
@app.route("/config/<ticket_type>", methods=["GET", "POST"])
def manage_config(ticket_type):
    config_path = f"configs/{ticket_type}.json"

    if not os.path.exists(config_path):
        return jsonify({"status": "error", "message": "Invalid ticket type or config not found."}), 400

    config_mgr = ConfigurationManager(config_file=config_path)

    if request.method == "GET":
        common, project = config_mgr.get_sources()
        return jsonify({"common": common, "project": project})

    if request.method == "POST":
        try:
            new_config = request.get_json()
            for key, value in new_config.items():
                config_mgr.set(key, value)
            return jsonify({"status": "success", "message": "Configuration updated."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/config-ui")
def config_ui():
    """
    Render the configuration management UI.
    """
    ticket_type = request.args.get("ticket_type", StringConstants.REGRESSION)
    return render_template("config-ui.html", ticket_type=ticket_type)


# Logging related endpoints
@app.route("/view-logs/<ticket_type>")
def view_logs(ticket_type):
    """
    View logs for a specific ticket type.
    """
    log_files = []

    for filename in os.listdir(LOGS_DIRECTORY):
        if filename.startswith(ticket_type):
            log_files.append(filename)

    log_files.sort(reverse=True)
    return render_template("logs.html", ticket_type=ticket_type, log_files=log_files)

@app.route("/download-log/<ticket_type>/<filename>")
def download_log_file(ticket_type, filename):
    """
    Download a specific log file for a ticket type.
    """
    if not filename.startswith(ticket_type):
        return abort(403, description="Unauthorized log file access.")

    log_path = os.path.join(LOGS_DIRECTORY, filename)

    if os.path.exists(log_path) and os.path.isfile(log_path):
        return send_file(log_path, as_attachment=True)
    else:
        return abort(404, description="Log file not found.")

@app.route("/view-log/<ticket_type>/<filename>")
def view_log_file(ticket_type, filename):
    """
    View contents of a specific log file in-browser.
    """
    if not filename.startswith(ticket_type):
        return abort(403, description="Unauthorized access.")

    log_path = os.path.join(LOGS_DIRECTORY, filename)

    if not os.path.exists(log_path):
        return abort(404, description="Log file not found.")

    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    return render_template("log_viewer.html", ticket_type=ticket_type, filename=filename, content=content)


# Token management endpoint
@app.route("/token-ui", methods=["GET", "POST"])
def token_ui():
    ticket_type = request.args.get("ticket_type", "regression")
    key_path = "credentials/secret.key"
    token_path = f"credentials/{StringConstants.TOKEN_PREFIX}{ticket_type}.txt"
    token_mgr = TokenManager(key_path, token_path)

    if request.method == "POST":
        try:
            mantis_token = request.form["mantis_token"]
            gitlab_token = request.form["gitlab_token"]
            token_mgr.save_tokens(mantis_token, gitlab_token)
            return render_template("token_ui.html", success=True, ticket_type=ticket_type)
        except Exception as e:
            return render_template("token_ui.html", error=str(e), ticket_type=ticket_type)

    return render_template("token_ui.html", ticket_type=ticket_type)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


