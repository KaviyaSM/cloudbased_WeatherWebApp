import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
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

document.getElementById("registerForm").addEventListener("submit", (event) => {
  event.preventDefault();

  const email = event.target.email.value;
  const password = event.target.password.value;

  createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      // Registration successful
      console.log("User registered:", userCredential.user);
      window.location.href = "login.html"; // redirect after success
    })
    .catch((error) => {
      document.getElementById("error-message").textContent = error.message;
      console.error("Error during registration:", error.code, error.message);
    });
});
