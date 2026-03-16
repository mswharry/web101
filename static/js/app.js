document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  if (!flashes.length) {
    return;
  }

  setTimeout(() => {
    flashes.forEach((item) => {
      item.style.opacity = "0";
      item.style.transition = "opacity 300ms ease";
    });
  }, 2500);
});
