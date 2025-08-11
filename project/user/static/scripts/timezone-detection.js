// Set user's timezone in the profile form input
document.addEventListener("DOMContentLoaded", function() {
  console.log("timezone js loaded")
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const tzInput = document.getElementById("id_timezone");
  if (tzInput) {
    tzInput.value = timezone;
    console.log("Set timezone:", timezone);
  }
  else {
    console.warn("No timezone input found");
  }
});