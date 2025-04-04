function showTreeDetails(element) {
    const name = element.dataset.name;
    const water = parseFloat(element.dataset.water);
    const waterRequired = parseFloat(element.dataset.waterRequired);
    const progress = waterRequired > 0 ? (water / waterRequired) * 100 : 0;

    // Update text content
    document.getElementById('treeDetailsTitle').textContent = name;
    document.getElementById('treeWater').textContent = water;
    document.getElementById('treeWaterRequired').textContent = waterRequired;
    
    // Update progress bar
    const progressBar = document.getElementById('treeProgressBar');
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
    document.getElementById('treeProgressText').textContent = `${water}/${waterRequired}`;

    // Toggle visibility
    document.getElementById('treeDetailsCard').classList.remove('d-none');
    document.getElementById('instruction').classList.add('d-none');
}

// Add event listeners
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-tree]').forEach(card => {
        card.addEventListener('click', () => showTreeDetails(card));
    });
});