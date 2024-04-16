var currentPath = window.location.pathname;
var navLinks = document.querySelectorAll('nav a');
navLinks.forEach(function(link) {
  if (link.getAttribute('href') === currentPath) {
    link.classList.add('active');
  }
});