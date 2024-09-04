function login_user() {
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    localStorage.setItem('login', login);
    localStorage.setItem('password', password);
}

localStorage.removeItem('login');
localStorage.removeItem('password');
const loginForm = document.getElementById('loginForm')
loginForm.addEventListener('submit', login_user)