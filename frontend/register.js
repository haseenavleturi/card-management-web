document.getElementById("registerForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (username === "") {
        alert("Please enter username.");
        return;
    }

    if (email === "") {
        alert("Please enter email.");
        return;
    }

    if (password === "") {
        alert("Please enter password.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return;
    }

    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Registration failed.");
            return;
        }

        alert("Registration successful!");

        window.location.href = "index.html";

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server.");
    }
});