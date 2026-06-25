// Frontend logic for Navigator AI Assistant
// AI GENERATED CODE

function uploadMessage(type, content) {
    const outputDiv = document.getElementById("message-history");
    if (!outputDiv) {
        console.error("Message history container not found!");
        return;
    }
    const div = document.createElement("div");
    let isAI = (type === 'AI');
    div.className = isAI
        ? "bg-white p-2 rounded-xl border-2 border-slate-200 shadow-sm"
        : "bg-nav-blue/5 p-2 rounded-xl border-l-8 border-primary";
    const p = document.createElement("p");
    p.className = "text-slate-900 font-reading large-text font-bold text-base";
    p.textContent = content;
    div.appendChild(p);
    outputDiv.appendChild(div);
    outputDiv.scrollTop = outputDiv.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
    const askBtn = document.getElementById("ask-btn");
    const textarea = document.querySelector("textarea");

    askBtn.addEventListener("click", function () {
        const question = textarea.value.trim();
        if (!question) return;
        uploadMessage('user', question);
        textarea.value = "";
        if (window.pywebview && window.pywebview.api && window.pywebview.api.ask) {
            window.pywebview.api.ask(question).then(function(data) {
                uploadMessage('AI', data.response);
            }).catch(function() {
                uploadMessage('AI', "Error: Could not reach backend.");
            });
        } else {
            uploadMessage('AI', "Error: pywebview API not available.");
        }
    });

    textarea.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            askBtn.click();
        }
    });

    // Read Aloud — speak the most recent message via the browser SpeechSynthesis API.
    const readAloudBtn = document.getElementById("read-aloud-btn");
    if (readAloudBtn) {
        readAloudBtn.addEventListener("click", function () {
            if (!("speechSynthesis" in window)) return;
            const messages = document.querySelectorAll("#message-history p");
            if (!messages.length) return;
            const lastMessage = messages[messages.length - 1].textContent.trim();
            if (!lastMessage) return;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(new SpeechSynthesisUtterance(lastMessage));
        });
    }
});
