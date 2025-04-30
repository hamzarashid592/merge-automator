async function loadConfig() {
  const response = await fetch("/code-move/config/data");
  const { common, project } = await response.json();
  const configForm = document.getElementById("configForm");

  const allConfigs = { ...common, ...project };
  const sourceMap = {};

  for (const key in common) sourceMap[key] = "common";
  for (const key in project) sourceMap[key] = "project";

  const renderedKeys = new Set();

  const configGroups = [
    {
      title: "General Settings",
      keys: ["PROJECT_ID", "STATUS_ID", "VIEW_STATE_ID"]
    },
    {
      title: "Target Options",
      keys: ["TARGET_VERSIONS", "TARGET_PATCHES", "QA_OWNERS"]
    },
    {
      title: "Defaults & Templates",
      keys: ["RECORD_TYPE", "INSTRUCTIONS_TEMPLATE", "ER_DATE_DEFAULT"]
    }
  ];


  for (const group of configGroups) {
    const header = document.createElement("h4");
    header.textContent = group.title;
    header.classList.add("mt-4", "mb-3");
    configForm.insertBefore(header, configForm.lastElementChild);

    group.keys.forEach((key) => {
      if (key in allConfigs) {
        renderedKeys.add(key);
        const div = createConfigInput(key, allConfigs[key], sourceMap[key]);
        configForm.insertBefore(div, configForm.lastElementChild);
      }
    });
  }

  const others = Object.keys(allConfigs).filter((key) => !renderedKeys.has(key));
  if (others.length > 0) {
    const otherHeader = document.createElement("h4");
    otherHeader.textContent = "Other";
    otherHeader.classList.add("mt-4", "mb-3");
    configForm.insertBefore(otherHeader, configForm.lastElementChild);

    others.forEach((key) => {
      const div = createConfigInput(key, allConfigs[key], sourceMap[key]);
      configForm.insertBefore(div, configForm.lastElementChild);
    });
  }
}


function createConfigInput(key, value, source) {
  const div = document.createElement("div");
  div.classList.add("mb-3");

  const label = document.createElement("label");
  label.classList.add("form-label");
  label.textContent = `${key} (${source === "common" ? "Shared Property" : "Code Move Property"})`;
  label.setAttribute("for", key);

  const input = document.createElement("input");
  input.type = key === "EXECUTION_TIME" ? "time" : "text";
  input.name = key;
  input.id = key;
  input.value = Array.isArray(value) ? value.join(" | ") : value;
  input.classList.add("form-control");
  input.readOnly = source === "common"; // lock common fields

  const toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.classList.add("btn", "btn-sm", "btn-outline-secondary", "ms-2");
  toggleBtn.textContent = source === "common" ? "Locked" : "Edit";
  toggleBtn.disabled = source === "common";
  toggleBtn.onclick = () => toggleEdit(input, toggleBtn);

  div.appendChild(label);
  div.appendChild(input);
  div.appendChild(toggleBtn);

  return div;
}


function toggleEdit(input, button) {
  input.readOnly = !input.readOnly;
  button.textContent = input.readOnly ? "Edit" : "Lock";
  input.classList.toggle("border", !input.readOnly);
  input.classList.toggle("border-2", !input.readOnly);
  input.classList.toggle("border-dark", !input.readOnly);
}

async function saveConfig(event) {
  event.preventDefault();
  const formData = new FormData(document.getElementById("configForm"));
  const configUpdate = {};

  for (const [key, value] of formData.entries()) {
    configUpdate[key] = isNaN(value) ? value : Number(value);
  }

  const response = await fetch("/code-move/config/data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(configUpdate)
  });

  const result = await response.json();
  alert(result.message);
}

window.onload = loadConfig;
