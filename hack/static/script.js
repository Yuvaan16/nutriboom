let progress = 0;
const progressBar = document.getElementById('progressBar');
const buttonContainer = document.getElementById('buttonContainer');

function increaseProgress() {
  if (progress < 100) {
    progress += 10;
    updateProgressBar();
  } else {
    progress = 0;
  }
}

function updateProgressBar() {
  progressBar.innerHTML = `<div class="fill" style="width: ${progress}%"></div>`;
}

function hideButtons() {
  buttonContainer.style.display = 'none';
  setTimeout(showButtons, 5000); // Show buttons after 10 seconds
}

function showButtons() {
  buttonContainer.style.display = 'block';
}
