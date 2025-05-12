document.addEventListener("DOMContentLoaded", () => {
    const statusBox = document.getElementById("status-box");
    const form = document.getElementById("config-form");
    const configSection = document.getElementById("common-config");

    function createInput(key, value) {
        const label = document.createElement("label");
        label.textContent = key;
        const input = document.createElement("input");
        input.type = "text";
        input.name = key;
        input.value = value;
        return [label, input];
    }

    function renderConfig(data, container) {
        container.innerHTML = "";
        Object.entries(data).forEach(([key, value]) => {
            const [label, input] = createInput(key, value);
            container.appendChild(label);
            container.appendChild(input);
        });
    }

    fetch("/config/common")
        .then(res => res.json())
        .then(data => {
            renderConfig(data, configSection);
            statusBox.textContent = "Common configuration loaded.";
        })
        .catch(() => {
            statusBox.textContent = "Error loading configuration.";
        });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const inputs = configSection.querySelectorAll("input");
        const updated = {};
        inputs.forEach(input => updated[input.name] = input.value);

        fetch("/config/common", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updated)
        })
        .then(res => res.json())
        .then(data => {
            statusBox.textContent = data.message || "Saved.";
        })
        .catch(() => {
            statusBox.textContent = "Error saving configuration.";
        });
    });
});
