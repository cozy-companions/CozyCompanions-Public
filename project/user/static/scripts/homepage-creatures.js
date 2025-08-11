// Animate preview creatures and handle notification bell/card logic
let previewGrid = getPreviewGrid();
let previewCreatures = getPreviewCreatures();
let timeoutId;

function getPreviewGrid() {
  return window.innerWidth <= 900
    ? document.querySelector(".mobile-layout .preview-grid")
    : document.querySelector(".desktop-layout .preview-grid");
}

function getPreviewCreatures() {
  return Array.from(previewGrid?.querySelectorAll(".preview-creature") || []);
}

function setInitialPosition(creature, index) {
  const gridRect = previewGrid.getBoundingClientRect();
  const gridWidth = gridRect.width;
  const gridHeight = gridRect.height;
  const img = creature.querySelector("img");
  const size = img ? Math.min(img.offsetWidth, img.offsetHeight) : 64;

  const marginX = Math.max(gridWidth * 0.05, 5);
  const marginY = Math.max(gridHeight * 0.05, 5);

  const maxX = gridWidth - size - marginX;
  const maxY = gridHeight - size - marginY;
  const x = Math.random() * (maxX - marginX) + marginX;
  const y = Math.random() * (maxY - marginY) + marginY;

  creature.style.left = `${x}px`;
  creature.style.top = `${y}px`;
}

function movePreviewCreatureRandomly(creature, index) {
  const gridRect = previewGrid.getBoundingClientRect();
  const gridWidth = gridRect.width;
  const gridHeight = gridRect.height;
  const img = creature.querySelector("img");
  const size = img ? Math.min(img.offsetWidth, img.offsetHeight) : 64;

  const marginX = Math.max(gridWidth * 0.05, 5);
  const marginY = Math.max(gridHeight * 0.05, 5);

  const maxX = gridWidth - size - marginX;
  const maxY = gridHeight - size - marginY;
  const x = Math.random() * (maxX - marginX) + marginX;
  const y = Math.random() * (maxY - marginY) + marginY;

  creature.style.transition = "all 4s ease-in-out";
  creature.style.left = `${x}px`;
  creature.style.top = `${y}px`;
  setTimeout(() => movePreviewCreatureRandomly(creature, index), 5000 + index * 1000);
}

function triggerNextAnimation() {
  previewCreatures.forEach((creature, index) => {
    setInitialPosition(creature, index);
    setTimeout(() => movePreviewCreatureRandomly(creature, index), 100);
  });
}

window.addEventListener("resize", () => {
  clearTimeout(timeoutId);
  previewGrid = getPreviewGrid();
  previewCreatures = getPreviewCreatures();
  triggerNextAnimation();
});

document.addEventListener("DOMContentLoaded", function () {
  // Initialize preview creatures logic
  previewCreatures.forEach((creature, index) => {
    creature.style.position = "absolute";
    creature.style.transition = "all 4s ease-in-out";
    creature.style.zIndex = "10";
    creature.style.cursor = "pointer";

    creature.addEventListener("click", () => {
      window.location.href = "/companions/";
    });

    setInitialPosition(creature, index);
    setTimeout(() => movePreviewCreatureRandomly(creature, index), 100);
  });

  // Notification Bell, Card, Blur, and Deactivation Logic
  const notificationBell = document.getElementById("notificationBell");
  const notificationCard = document.getElementById("notification-card");
  const mainNavbar = document.getElementById('main-navbar');
  const contentWrapper = document.getElementById('content-wrapper');

  // Create or get the overlay div
  let overlay = document.getElementById('notification-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'notification-overlay';
    document.body.appendChild(overlay);
  }
  
  let isCardOpen = false;

  // Function to close the notification card
  function closeNotificationCard() {
    notificationCard.style.display = 'none';
    contentWrapper.classList.remove('blurred-content');
    overlay.style.display = 'none';
    deactivateInteractiveElements(false);
    isCardOpen = false;
  }

  // Function to open the notification card
  function openNotificationCard() {
    notificationCard.style.display = 'block';
    contentWrapper.classList.add('blurred-content');
    overlay.style.display = 'block';
    deactivateInteractiveElements(true);
    isCardOpen = true;
  }

  // Set initial display states (hidden by default)
  if (notificationCard) {
    notificationCard.style.display = 'none';
  }
  if (overlay) {
    overlay.style.display = 'none';
  }

  if (notificationBell && notificationCard && mainNavbar && contentWrapper && overlay) {
    notificationBell.addEventListener("click", function (event) {
      event.stopPropagation();
      if (isCardOpen) {
        closeNotificationCard();
      } else {
        openNotificationCard();
      }
    });

  // Close when clicking outside notification card/bell
  document.addEventListener("click", function (event) {
  const isClickInsideCard = event.target.closest('#notification-card');

  if (!isClickInsideCard && notificationCard.style.display !== 'none') {
    notificationCard.style.display = 'none';
    contentWrapper.classList.remove('blurred-content');
    overlay.style.display = 'none';
    deactivateInteractiveElements(false);
  }
  });

    // Function to activate/deactivate buttons and links
    function deactivateInteractiveElements(disable) {
      const allInteractiveElements = document.querySelectorAll(
        'button, a, input, select, textarea'
      );

      allInteractiveElements.forEach(element => {
        if (!mainNavbar.contains(element) && !notificationCard.contains(element)) {
          if (disable) {
            element.classList.add('deactivated');
            if (element.tagName === 'BUTTON' || element.tagName === 'INPUT' || element.tagName === 'SELECT' || element.tagName === 'TEXTAREA') {
              element.setAttribute('disabled', 'true');
            }
          } else {
            element.classList.remove('deactivated');
            if (element.hasAttribute('disabled')) {
              element.removeAttribute('disabled');
            }
          }
        }
      });
    }

  } else {
    console.error('ERROR: Missing one or more required elements for notification/blur functionality. Check console logs for "null" elements.');
  }
});