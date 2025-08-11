document.addEventListener('DOMContentLoaded', () => {
  const contentWrapper = document.querySelector('.content-wrapper');
  const { feedUrl, toggleSelectedUrl, csrfToken } = window.DJANGO_DATA || {};
  if (!feedUrl || !toggleSelectedUrl || !csrfToken) {
    console.error("Missing Django data:", window.DJANGO_DATA);
    return;
  }

  checkFeedAllButtonStatus();
  if (document.getElementById('active-grid-wrapper')) {
    animateCreatures();
  }
  setupEventListeners();

  function setupEventListeners() {
    document.addEventListener('click', async (e) => {
      if (e.target.matches('.feed-btn')) {
        await handleFeed(e.target);
      }
      else if (e.target.matches('.toggle-btn')) {
        await handleToggle(e.target);
      }
      else if (e.target.matches('.wake-btn')) {
        await handleWakeUp(e.target);
      }
      else if (e.target.closest('.unselect-cross')) {
        const btn = e.target.closest('.unselect-cross');
        await handleUnselectFromCard(btn.dataset.ucId);
      }
    });

    // Feed All button
    document.getElementById('feed-all')?.addEventListener('click', handleFeedAll);
  }

  //Creature Movement//
  function animateCreatures() {
    const activeGrid = document.getElementById('active-grid-wrapper');
    if (!activeGrid) return;

    const activeCards = activeGrid.querySelectorAll('.creature-card');
    activeCards.forEach((card, index) => {
      card.style.position = 'absolute';
      card.style.transition = 'all 4s ease-in-out';
      card.style.zIndex = '10';
      card.style.cursor = 'pointer';

      card.addEventListener('click', handleActiveCreatureClick);
      moveCreatureRandomly(card, index);
    });
  }

  function moveCreatureRandomly(card, index) {
    const grassland = document.getElementById('active-grid-wrapper');
    if (!grassland) return;

    const rect = grassland.getBoundingClientRect();
    const img = card.querySelector('img');
    const imgSize = img ? Math.min(img.offsetWidth, img.offsetHeight) : 80;

    // Calculate position within quadrant
    const row = Math.floor(index / 2);
    const col = index % 2;
    const sectionWidth = rect.width / 2;
    const sectionHeight = rect.height / 2;

    const minX = col * sectionWidth;
    const maxX = minX + sectionWidth - imgSize;
    const minY = row * sectionHeight;
    const maxY = minY + sectionHeight - imgSize;

    // Apply padding
    const paddingX = Math.max(5, rect.width * 0.05);
    const paddingY = Math.max(5, rect.height * 0.05);

    const randomX = Math.random() * (maxX - minX) + minX;
    const randomY = Math.random() * (maxY - minY) + minY;

    card.style.left = `${randomX}px`;
    card.style.top = `${randomY}px`;

    card.movementTimeout = setTimeout(() => {
      moveCreatureRandomly(card, index);
    }, 2000 + Math.random() * 4000);
  }

  async function handleToggle(btn) {
    btn.disabled = true;
    try {
      const mainCard = document.getElementById(`card-${btn.dataset.ucId}`);
    if (mainCard && mainCard.classList.contains('hibernating')) {
      showError("Cannot select hibernating creatures");
      return;
    }
      const response = await fetch(toggleSelectedUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ uc_id: btn.dataset.ucId })
      });

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      // Update UI
      const isSelected = btn.classList.contains('unselect-btn');
      btn.textContent = isSelected ? "Select" : "Unselect";
      btn.classList.toggle("select-btn");
      btn.classList.toggle("unselect-btn");

      updateSelectedCreaturesCards(btn.dataset.ucId, isSelected);
      updateActiveGrid(btn.dataset.ucId, isSelected);
      window.location.reload();
      animateCreatures();
    } catch (error) {
      showError(error.message);
    } finally {
      btn.disabled = false;
    }
  }

  async function handleFeed(btn) {
    btn.disabled = true;
    try {
      const response = await fetch(feedUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ uc_id: btn.dataset.ucId })
      });

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      // Update UI
      const card = document.getElementById(`card-${btn.dataset.ucId}`);
      if (card) {
        card.querySelector('.hunger-fill').style.width = "0%";
        card.querySelector('.status-text').textContent = "Content";
        btn.textContent = "Fed";
        btn.disabled = true;
      }
      checkFeedAllButtonStatus();
    } catch (error) {
      showError(error.message);
      btn.disabled = false;
    }
  }

  async function handleWakeUp(btn) {
    btn.disabled = true;
    btn.textContent = "Waking...";
    try {
      const response = await fetch(`/companions/wake/${btn.dataset.ucId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ uc_id: btn.dataset.ucId })
      });

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      window.location.reload();
    } catch (error) {
      showError(error.message);
      btn.disabled = false;
      btn.textContent = "Wake Up";
    }
  }

  //UI updates//
  function updateSelectedCreaturesCards(ucId, isCurrentlySelected) {
    const container = document.querySelector('.selected-creatures-cards');
    if (!container) return;

    if (isCurrentlySelected) {
      const card = container.querySelector(`[data-uc-id="${ucId}"]`);
      if (card) card.remove();
    } else {
      const mainCard = document.getElementById(`card-${ucId}`);
      if (!mainCard || mainCard.classList.contains('hibernating')) return;

      const newCard = document.createElement('div');
      newCard.className = 'small-creature-card';
      newCard.dataset.ucId = ucId;
      newCard.innerHTML = `
        <img src="${mainCard.dataset.iconUrl}" alt="${mainCard.querySelector('h3').textContent}">
        <button class="unselect-cross" data-uc-id="${ucId}">
          <span>&times;</span>
        </button>
      `;
      container.appendChild(newCard);
    }
    window.location.reload();
  }

  function updateActiveGrid(ucId, isCurrentlySelected) {
    const grid = document.getElementById('active-grid-wrapper');
    if (!grid) return;

    if (isCurrentlySelected) {
      const card = document.getElementById(`active-card-${ucId}`);
      if (card) card.remove();
    } else {
      const mainCard = document.getElementById(`card-${ucId}`);
      if (!mainCard) return;

      if (mainCard.classList.contains('hibernating')) {
        return; // Don't add to active grid if hibernating
      }

      const newCard = document.createElement('div');
      newCard.className = 'creature-card';
      newCard.id = `active-card-${ucId}`;
      newCard.innerHTML = `<img src="${mainCard.dataset.iconUrl}" alt="Selected Creature">`;
      grid.appendChild(newCard);
    }
    animateCreatures();
  }

  function checkFeedAllButtonStatus() {
    const feedAllBtn = document.getElementById('feed-all');
    if (!feedAllBtn) return;

    const canFeed = document.querySelectorAll('.feed-btn:not(:disabled)').length > 0;
    feedAllBtn.disabled = !canFeed;
    feedAllBtn.textContent = canFeed ? "Feed All" : "All Fed";
    feedAllBtn.classList.toggle('disabled-feed-all', !canFeed);
  }

  //Helper//
  async function handleUnselectFromCard(ucId) {
  try {
    const response = await fetch(window.DJANGO_DATA.toggleSelectedUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": window.DJANGO_DATA.csrfToken,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({ uc_id: ucId })
    });

    const data = await response.json();
    
    if (data.error) {
      showError(data.error);
      return;
    }

    // Remove small selected card
    const smallCard = document.querySelector(`.small-creature-card[data-uc-id="${ucId}"]`);
    if (smallCard) smallCard.remove();

    // Update main grid button
    const mainCard = document.getElementById(`card-${ucId}`);
    if (mainCard) {
      const toggleBtn = mainCard.querySelector('.toggle-btn');
      if (toggleBtn) {
        toggleBtn.textContent = "Select";
        toggleBtn.classList.remove("unselect-btn");
        toggleBtn.classList.add("select-btn");
      }
    }

    // Remove from active grid
    const activeCard = document.getElementById(`active-card-${ucId}`);
    if (activeCard) activeCard.remove();

    window.location.reload();
    
  } catch (error) {
    console.error("Unselect error:", error);
    showError("Failed to unselect creature");
  }
}


  function showError(message) {
    const errorBox = document.getElementById('error-message');
    if (errorBox) {
      errorBox.textContent = message;
      errorBox.style.display = 'block';
    } else {
      alert(message);
    }
  }

  function handleActiveCreatureClick(e) {
    const card = e.currentTarget;
    const creatureId = card.id.replace('active-card-', '');
    const mainCard = document.getElementById(`card-${creatureId}`);
    
    if (!mainCard) return;

    showCreatureDetailsCard(
      mainCard.querySelector('h3').textContent,
      creatureId,
      mainCard.querySelector('img').src,
      mainCard.querySelector('h4').textContent
    );
  }

  function showCreatureDetailsCard(name, id, imageSrc, level) {
    const mainCard = document.getElementById(`card-${id}`);
    if (mainCard && mainCard.classList.contains('hibernating')) {
      showError("This creature is hibernating");
      return;
    }
    //Remove existing modals
    document.querySelectorAll('.creature-details-overlay').forEach(el => el.remove());

    const overlay = document.createElement('div');
    overlay.className = 'creature-details-overlay';
    overlay.innerHTML = `
      <div class="creature-details-card">
        <button class="close-details-btn">&times;</button>
        <img src="${imageSrc}" alt="${name}" class="creature-details-img">
        <h3 class="creature-details-name">${name}</h3>
        <h4 class="creature-details-level">${level}</h4>
        <div class="creature-details-buttons">
          <button class="creature-action details-feed-btn" data-uc-id="${id}">Feed</button>
          <button class="creature-action details-unselect-btn" data-uc-id="${id}">Unselect</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    //Add event listeners
    overlay.querySelector('.close-details-btn').addEventListener('click', () => overlay.remove());
    overlay.querySelector('.details-feed-btn').addEventListener('click', async () => {
      await handleFeed(overlay.querySelector('.details-feed-btn'));
      overlay.remove();
    });
    overlay.querySelector('.details-unselect-btn').addEventListener('click', async () => {
      await handleUnselectFromCard(id);
      overlay.remove();
    });
  }

  async function handleFeedAll() {
    const btn = this;
    btn.disabled = true;
    btn.textContent = "Feeding...";

    const feedButtons = Array.from(document.querySelectorAll('.feed-btn:not(:disabled)'));
    for (const feedBtn of feedButtons) {
      await handleFeed(feedBtn);
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    btn.textContent = "Feed All";
    btn.disabled = false;
    checkFeedAllButtonStatus();
  }
});