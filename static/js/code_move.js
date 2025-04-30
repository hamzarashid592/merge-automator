document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const startBtn = document.getElementById("startBtn");
    const progressContainer = document.getElementById("progressContainer");
    const progressBar = document.getElementById("progressBar");
    const statusText = document.getElementById("statusText");
  
    // Populate dropdowns dynamically
    fetch("/code-move/options")
      .then((response) => response.json())
      .then((options) => {
        populateSelect("qa_owner", options.qa_owners);
        populateSelect("target_version", options.target_versions);
        populateSelect("target_patch", options.target_patches);
      });
  
    function populateSelect(id, values) {
      const select = document.getElementById(id);
      if (!select) return;
      select.innerHTML = ""; // clear existing options
  
      const defaultOption = document.createElement("option");
      defaultOption.text = "-- Select --";
      defaultOption.value = "";
      select.appendChild(defaultOption);
  
      values.forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      });
    }
  
    // Progress polling
    form.addEventListener("submit", () => {
      startBtn.disabled = true;
      startBtn.textContent = "Cloning...";
      progressContainer.style.display = "block";
  
      const interval = setInterval(() => {
        fetch("/code-move/progress")
          .then((response) => response.json())
          .then((progress) => {
            progressBar.style.width = `${progress.percentage}%`;
            progressBar.textContent = `${progress.percentage}%`;
            statusText.textContent = `Status: ${progress.status}`;
  
            if (
              progress.status === "completed" ||
              progress.status.startsWith("error")
            ) {
              clearInterval(interval);
              startBtn.disabled = false;
              startBtn.textContent = "Start Clone";
            }
          });
      }, 1000);
    });
  });
  