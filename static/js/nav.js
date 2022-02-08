const openBtn = document.querySelector(".open-btn");
const cookieBox = document.querySelector(".cookie-box");
const closeBtn = document.querySelector(".close-btn");

const navSlide = () => {
  const burger = document.querySelector(".burger");
  const nav = document.querySelector(".nav-links");
  const navLinks = document.querySelectorAll(".nav-links li");
  burger.addEventListener("click", () => {
    //here we add toggle rather than add to in and out with same button
    nav.classList.toggle("nav-active");
    //to make evrything off
    //animate links
    navLinks.forEach((link, index) => {
      if (link.style.animation) {
        link.style.animation = " ";
      } else {
        link.style.animation = `navLinkFade 0.5s ease forwards ${
          index / 7 + 0.3
        }s`;
      }
    });
    //burger ANimation
    burger.classList.toggle("toggle");
  });
};
navSlide();

openBtn.addEventListener("click", () => {
  cookieBox.classList.add("active");
});

closeBtn.addEventListener("click", () => {
  cookieBox.classList.remove("active");
});

const options = document.querySelector(".options");
const dropdown = document.querySelector(".dropdown");

options.addEventListener("click", () => {});
