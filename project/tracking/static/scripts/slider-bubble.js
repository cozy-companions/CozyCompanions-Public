// Slider bubble logic for questionnaire detail page
document.addEventListener('DOMContentLoaded', function () {
  const sliderContainers = document.querySelectorAll('.slider-container');

  sliderContainers.forEach(function (container) {
    const slider = container.querySelector('input[type="range"].slider');
    const bubble = container.querySelector('.slider-bubble');
    if (!slider || !bubble) return;

    // Set slider track color based on value
    function setSliderTrackColor(slider) {
      const min = Number(slider.min) || 1;
      const max = Number(slider.max) || 10;
      const val = Number(slider.value);
      const percent = ((val - min) / (max - min)) * 100;
      slider.style.background = `linear-gradient(to right, #ff69b4 0%, #ff69b4 ${percent}%, #fff ${percent}%, #fff 100%)`;
    }

    slider.oninput = function () {
      bubble.innerHTML = this.value;
      setSliderTrackColor(this);
    }

    // Set initial color
    setSliderTrackColor(slider);
  });
}); 