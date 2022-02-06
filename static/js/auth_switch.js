const signinBtn = document.querySelector('#sign-in-btn');
const signupBtn = document.querySelector('#sign-up-btn');
const container = document.querySelector('.container');

signupBtn.addEventListener('click', () => {
  container.classList.add('sign-up-mode');
});

signinBtn.addEventListener('click', () => {
  container.classList.remove('sign-up-mode');
});