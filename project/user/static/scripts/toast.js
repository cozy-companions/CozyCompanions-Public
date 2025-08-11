// Toast auto-hide logic for notification messages
document.addEventListener('DOMContentLoaded', () => {
  const toastContainer = document.getElementById('toast-container');
  
  if (toastContainer) {
    setTimeout(() => {
      toastContainer.querySelectorAll('.toast').forEach(toast => {
        toast.classList.add('is-hidden');
      });
      
      setTimeout(() => {
          toastContainer.innerHTML = '';
      }, 500);
      
    }, 3000);
  }
});