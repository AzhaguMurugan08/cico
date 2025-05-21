const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});


    function togglePasskeyField() {
        const role = document.getElementById("login-role").value;
        const passkeyField = document.getElementById("passkey");
        const passkeyLabel = document.getElementById("passkey-label");

        if (role === "staff") {
            passkeyField.style.display = "block";
            passkeyLabel.style.display = "block";
            passkeyField.setAttribute("required", "required");
        } else {
            passkeyField.style.display = "none";
            passkeyLabel.style.display = "none";
            passkeyField.removeAttribute("required");
        }
    }

    // Initialize the field visibility on page load
    window.onload = function () {
        togglePasskeyField();
        toggleSignupUserFields();
    };

    function toggleSignupUserFields() {
        const role = document.getElementById("signup-role").value;
        const batchField = document.getElementById("signup-batch");
        const ageField = document.getElementById("signup-age");
        const addressField = document.getElementById("signup-address");

        if (role === "user") {
            // Show fields for Watchman
            batchField.style.display = "block";
            ageField.style.display = "block";
            addressField.style.display = "block";

            // Make fields required
            batchField.setAttribute("required", "required");
            ageField.setAttribute("required", "required");
            addressField.setAttribute("required", "required");
        } else {
            // Hide fields for other roles
            batchField.style.display = "none";
            ageField.style.display = "none";
            addressField.style.display = "none";

            // Remove required attribute
            batchField.removeAttribute("required");
            ageField.removeAttribute("required");
            addressField.removeAttribute("required");
        }
    }
