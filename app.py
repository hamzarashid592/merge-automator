from flask import Flask, render_template, send_file, abort, jsonify, request
import json
import threading
import merge_automation 
import os

app = Flask(__name__)

# Paths to log directories
LOGS_DIRECTORY = "logs"
LOG_TYPES = {
    "git": "git",
    "mantis": "mantis",
    "merge-analytics": "merge_analytics"
}
CONFIG_FILE = "config.json"

@app.route("/")
def home():
    """
    Home page displaying options to trigger the job and view logs.
    """
    return render_template("index.html")

@app.route("/view-logs/<log_type>")
def view_logs(log_type):
    """
    View logs of the specified type, listed by file.
    """
    LOGS_DIRECTORY = "logs"
    LOG_TYPES = {"git": "git", "mantis": "mantis", "merge-analytics": "merge_analytics"}

    # Validate log type
    if log_type not in LOG_TYPES:
        return abort(404, description="Log type not found.")

    log_files = []
    log_path = LOGS_DIRECTORY

    # Get all files for the specified log type
    for filename in os.listdir(log_path):
        if filename.startswith(LOG_TYPES[log_type]):
            log_files.append(filename)

    # Sort log files by date
    log_files.sort(reverse=True)

    # Render the logs page
    return render_template("logs.html", log_type=log_type, log_files=log_files)


@app.route("/download-log/<log_type>/<filename>")
def download_log_file(log_type, filename):
    """
    Download a specific log file.
    """
    LOGS_DIRECTORY = "logs"
    LOG_TYPES = {"git": "git", "mantis": "mantis", "merge-analytics": "merge_analytics"}

    # Validate log type
    if log_type not in LOG_TYPES:
        return abort(404, description="Log type not found.")

    log_path = os.path.join(LOGS_DIRECTORY, filename)

    # Ensure the file exists and is within the log directory
    if os.path.exists(log_path) and os.path.isfile(log_path):
        return send_file(log_path, as_attachment=True)
    else:
        return abort(404, description="Log file not found.")


@app.route("/trigger-job", methods=["GET", "POST"])
def trigger_job():
    """
    Endpoint to trigger the merge automation job.
    """
    if merge_automation.progress["status"] == "running":
        return jsonify({"status": "error", "message": "Job is already running."}), 400

    # Run the automation in a separate thread
    threading.Thread(target=merge_automation.automate_regression_merging).start()
    return jsonify({"status": "success", "message": "Job started."})

# Fetch the current progress
@app.route("/progress", methods=["GET"])
def get_progress():
    """
    Endpoint to fetch the current progress of the job.
    """
    return jsonify(merge_automation.progress)

# Load configuration
def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

# Save configuration
def save_config(new_config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(new_config, file, indent=4)

@app.route("/config", methods=["GET"])
def get_config():
    """
    Fetch the current configuration.
    """
    config = load_config()
    return jsonify(config)

@app.route("/config", methods=["POST"])
def update_config():
    """
    Update the configuration.
    """
    try:
        new_config = request.json
        save_config(new_config)
        return jsonify({"status": "success", "message": "Configuration updated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/config-ui")
def config_ui():
    """
    Render the configuration management UI.
    """
    return render_template("config.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


