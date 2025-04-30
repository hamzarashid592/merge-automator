document.addEventListener("DOMContentLoaded", () => {
    const statusBox = document.getElementById("status-box");
    const form = document.getElementById("config-form");
    const commonSection = document.getElementById("common-config");
    const projectSection = document.getElementById("project-config");

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

    fetch(`/config/${ticketType}`)
        .then(res => res.json())
        .then(data => {
            renderConfig(data.common, commonSection);
            renderConfig(data.project, projectSection);
            statusBox.textContent = "Configuration loaded.";
        })
        .catch(() => {
            statusBox.textContent = "Error loading configuration.";
        });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const inputs = form.querySelectorAll("input");
        const updated = {};
        inputs.forEach(input => updated[input.name] = input.value);

        fetch(`/config/${ticketType}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updated)
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                statusBox.textContent = "Configuration saved.";
            } else {
                statusBox.textContent = `Error: ${data.message}`;
            }
        })
        .catch(() => {
            statusBox.textContent = "Error saving configuration.";
        });
    });
});
