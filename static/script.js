document.getElementById("summaryForm").addEventListener("submit", function () {
  const submitButton = document.getElementById("submitButton");
  
  // Add loading class to trigger CSS animation
  submitButton.classList.add("button-loading");
  
  // Disable the button
  submitButton.disabled = true;
  
  // Change text
  submitButton.innerText = "Summarizing...";
});
