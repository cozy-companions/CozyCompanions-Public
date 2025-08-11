// Dynamic hobbies add/remove logic for profile forms
document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById("add-hobby-btn");
    const hobbyInput = document.getElementById("new-hobby-input");
    const hobbyListDiv = document.getElementById("dynamic-hobbies-list");
    const hiddenHobbiesInput = document.getElementById("hobbies-json-input");

    // This check stops the script if any required HTML element is missing.
    if (!addButton || !hobbyInput || !hobbyListDiv || !hiddenHobbiesInput) {
        return;
    }

    let hobbies = [];

    // Update the hidden input with the current hobbies array
    function updateHiddenInput() {
        hiddenHobbiesInput.value = JSON.stringify(hobbies);
    }

    // Render a hobby tag with remove button
    function renderHobbyTag(hobbyName) {
        const hobbyTag = document.createElement('div');
        hobbyTag.className = 'hobby-item';
        hobbyTag.textContent = hobbyName;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = "remove-hobby-btn";
        removeBtn.innerHTML = '&#10060;'; 
        
        removeBtn.onclick = function() {
            hobbies = hobbies.filter(h => h !== hobbyName);
            hobbyTag.remove();
            updateHiddenInput();
        };

        hobbyTag.appendChild(removeBtn);
        hobbyListDiv.appendChild(hobbyTag);
    }

    // --- INITIALIZATION (for the update page) ---
    const hobbiesDataElement = document.getElementById('initial-hobbies-data');
    if (hobbiesDataElement) {
        const initialHobbies = JSON.parse(hobbiesDataElement.textContent);
        initialHobbies.forEach(hobbyName => {
            hobbies.push(hobbyName);
            renderHobbyTag(hobbyName);
        });
        updateHiddenInput();
    }

    // --- EVENT LISTENERS ---
    addButton.addEventListener("click", () => {
        const hobbyName = hobbyInput.value.trim();
        if (hobbyName && !hobbies.includes(hobbyName) && hobbies.length < 5) {
            hobbies.push(hobbyName);
            renderHobbyTag(hobbyName);
            updateHiddenInput();
            hobbyInput.value = '';
        } else if (hobbies.length >= 5) {
            alert("You can add a maximum of 5 hobbies.");
        }
    });

    hobbyInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            addButton.click();
        }
    });
});