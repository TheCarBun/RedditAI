document.getElementById("summaryForm").addEventListener("submit", function () {
  // Show the spinner
  document.getElementById("loadingSpinner").style.display = "block";
  // Disable the submit button to prevent multiple submissions
  const submitButton = document.getElementById("submitButton");
  submitButton.disabled = true;
  submitButton.value = "Summarizing..."; // Change button text
});
