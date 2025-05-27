import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import {
  getAuth,
  signInWithEmailAndPassword,
} from "https://www.gstatic.com/firebasejs/11.8.1/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBgm57Ar1QQaObKYiQX_pAlp91wgrKBIjk",
  authDomain: "cloudbased-weatherwebapp.firebaseapp.com",
  projectId: "cloudbased-weatherwebapp",
  storageBucket: "cloudbased-weatherwebapp.firebasestorage.app",
  messagingSenderId: "182211103239",
  appId: "1:182211103239:web:454d8cee6422728d6738a2",
};
// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // Signed in
        const user = userCredential.user;
        console.log("Login successful:", user);
        // Redirect to the weather app
        window.location.href = "weather.html"; // Change to your weather app page
      })
      .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        document.getElementById("error-message").innerText = errorMessage;
        console.error("Error during login:", errorCode, errorMessage);
      });
  });
