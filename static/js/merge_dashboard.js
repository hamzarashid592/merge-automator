// Handle tab switching
const tabs = document.querySelectorAll('.tab');
const sections = document.querySelectorAll('.section');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        sections.forEach(s => s.classList.remove('active'));

        tab.classList.add('active');
        const section = document.getElementById(tab.dataset.type);
        if (section) section.classList.add('active');
    });
});

// Trigger merge job
function triggerMerge(type) {
    const button = document.getElementById(`${type}-btn`);
    const status = document.getElementById(`${type}-status`);

    button.disabled = true;
    status.textContent = "Starting...";

    fetch(`/trigger-job/${type}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            status.textContent = data.message;
            if (data.status === 'success') pollProgress(type);
            else button.disabled = false;
        })
        .catch(() => {
            status.textContent = "Error starting job";
            button.disabled = false;
        });
}

// Poll progress
function pollProgress(type) {
    const status = document.getElementById(`${type}-status`);
    const button = document.getElementById(`${type}-btn`);

    const interval = setInterval(() => {
        fetch(`/progress/${type}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'completed') {
                    status.textContent = "Completed!";
                    button.disabled = false;
                    clearInterval(interval);
                } else if (data.status?.startsWith("error")) {
                    status.textContent = `Error: ${data.status}`;
                    button.disabled = false;
                    clearInterval(interval);
                } else {
                    status.textContent = `Running... ${data.percentage}%`;
                }
            });
    }, 3000);
}
