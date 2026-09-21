document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const loginInput = document.getElementById("loginInput").value.trim();
    const password = document.getElementById("password").value.trim();

    if (loginInput === "" || password === "") {
        alert("Please enter username/email and password.");
        return;
    }

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: loginInput,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Login failed");
            return;
        }

        // Save logged-in user
        localStorage.setItem("userId", data.user.id);

        // Open Dashboard
        window.location.href = "home.html";

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server.");
    }
});