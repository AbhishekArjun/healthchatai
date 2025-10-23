document.addEventListener("DOMContentLoaded", function() {
    // Chat elements
    const sendBtn = document.getElementById("send");
    const input = document.getElementById("user-input");
    const chatLog = document.getElementById("chat-log");

    // Booking & toast elements
    const bookBtn = document.getElementById("book");
    const toastEl = document.getElementById("booking-toast");
    const toastMessage = document.getElementById("toast-message");
    const toast = new bootstrap.Toast(toastEl);

    // Doctor search/filter elements
    const specialtySelect = document.getElementById("doctor-specialty");
    const locationSelect = document.getElementById("doctor-location");
    const doctorQueryInput = document.getElementById("doctor-query");
    const doctorResults = document.getElementById("doctor-results");

    let allDoctors = []; // Last fetched doctors

    // Suggested symptoms (clickable badges)
    const suggestions = ["Fever", "Cold", "Headache", "Cough", "Fatigue"];
    const suggestionsDiv = document.getElementById("suggestions");
    if(suggestionsDiv){
        suggestionsDiv.innerHTML = "";
        suggestions.forEach(symptom => {
            const span = document.createElement("span");
            span.className = "badge bg-primary me-1 suggestion";
            span.innerText = symptom;
            span.style.cursor = "pointer";
            span.addEventListener("click", () => sendMessage(symptom));
            suggestionsDiv.appendChild(span);
        });
    }

    // Add message to chat log
    function addMessage(sender, text) {
        const div = document.createElement("div");
        div.classList.add("message", sender === "You" ? "user-message" : "bot-message");
        div.innerHTML = text.replace(/\n/g, "<br>");
        chatLog.appendChild(div);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // Typing indicator
    function showTyping() {
        const typingDiv = document.createElement("div");
        typingDiv.id = "typing-indicator";
        typingDiv.classList.add("bot-message");
        typingDiv.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
        chatLog.appendChild(typingDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function removeTyping() {
        const typingDiv = document.getElementById("typing-indicator");
        if (typingDiv) typingDiv.remove();
    }

    // Send chat message
    async function sendMessage(msg = null) {
        const text = msg || input.value.trim();
        if (!text) {
            toastMessage.innerText = "Please enter a message!";
            toast.show();
            return;
        }

        addMessage("You", text);
        input.value = "";
        showTyping();

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            setTimeout(() => {
                removeTyping();
                addMessage("AI", data.reply || "No reply from AI.");
            }, 800 + Math.random() * 800);
        } catch (e) {
            removeTyping();
            addMessage("AI", "Sorry, something went wrong. Try again.");
            toastMessage.innerText = "Error sending message!";
            toast.show();
        }
    }

    sendBtn.addEventListener("click", () => sendMessage());
    input.addEventListener("keypress", e => { if (e.key === "Enter") sendMessage(); });

    // Fetch doctors based on filters
    async function fetchDoctors() {
        const specialty = specialtySelect.value;
        const location = locationSelect.value;
        try {
            const res = await fetch(`/find_doctor?specialty=${encodeURIComponent(specialty)}&location=${encodeURIComponent(location)}`);
            const data = await res.json();
            allDoctors = data.doctors || [];
            filterDoctors();
        } catch (err) {
            console.error("Error fetching doctors:", err);
            toastMessage.innerText = "Error fetching doctors!";
            toast.show();
        }
    }

    // Filter doctors based on search input
    function filterDoctors() {
        const query = doctorQueryInput.value.toLowerCase().trim();
        doctorResults.innerHTML = "";

        if (!allDoctors.length) {
            doctorResults.style.display = "none"; // Hide list if no doctors
            return;
        }

        const filtered = allDoctors.filter(d =>
            d.name.toLowerCase().includes(query) ||
            d.specialty.toLowerCase().includes(query) ||
            d.location.toLowerCase().includes(query)
        );

        if (filtered.length === 0) {
            doctorResults.style.display = "block";
            const li = document.createElement("li");
            li.className = "list-group-item text-muted";
            li.textContent = "No doctors found.";
            doctorResults.appendChild(li);
            return;
        }

        doctorResults.style.display = "block"; // Show results
        filtered.forEach(d => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = `${d.name} — ${d.specialty} (${d.location}) <button class="btn btn-sm btn-outline-success book-btn">Book</button>`;
            doctorResults.appendChild(li);

            li.querySelector(".book-btn").addEventListener("click", () => {
                document.getElementById("pdoctor").value = d.name;
                document.getElementById("pname").focus();
            });
        });
    }

    // Event listeners
    specialtySelect.addEventListener("change", fetchDoctors);
    locationSelect.addEventListener("change", fetchDoctors);
    doctorQueryInput.addEventListener("input", () => {
        if (!doctorQueryInput.value.trim()) {
            doctorResults.innerHTML = "";
            doctorResults.style.display = "none"; // Hide when search is empty
        } else {
            filterDoctors();
        }
    });
    document.getElementById("search-doctor")?.addEventListener("click", fetchDoctors);

    // Book appointment
    bookBtn.addEventListener("click", async () => {
        const name = document.getElementById("pname").value;
        const doctor = document.getElementById("pdoctor").value;
        const date = document.getElementById("pdate").value;
        const time = document.getElementById("ptime").value;

        if (!name || !doctor || !date || !time) {
            toastMessage.innerText = "Please fill all booking fields!";
            toast.show();
            return;
        }

        try {
            const res = await fetch("/book", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, doctor, date, time })
            });
            const data = await res.json();
            toastMessage.innerText = data.message || data.error || "Booking completed!";
            toast.show();
        } catch (err) {
            console.error("Booking error:", err);
            toastMessage.innerText = "Error booking appointment!";
            toast.show();
        }
    });

    // Initial state
    allDoctors = [];
    doctorResults.innerHTML = "";
    doctorResults.style.display = "none"; // Hidden initially
});
