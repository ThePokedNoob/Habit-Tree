function showTreeDetails(element) {
    const index = element.dataset.index;
    const name = element.dataset.name;
    const water = element.dataset.water;
    const stage = element.dataset.stage;
    const waterRequired = element.dataset.waterRequired;

    // Update details card
    document.getElementById('treeDetailsTitle').value = name;
    document.getElementById('treeStage').textContent = `Stage: ${stage}`;
    document.getElementById('treeWater').textContent = water;
    document.getElementById('treeWaterRequired').textContent = waterRequired;
    const progress = (water / waterRequired * 100).toFixed(2);
    document.getElementById('treeProgressBar').style.width = `${progress}%`;
    document.getElementById('treeProgressText').textContent = `${water}/${waterRequired}`;

    // Store index in the details card
    document.getElementById('treeDetailsCard').dataset.index = index;

    // Toggle visibility
    document.getElementById('treeDetailsCard').classList.remove('d-none');
    document.getElementById('instruction').classList.add('d-none');
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-tree]').forEach(card => {
        card.addEventListener('click', () => showTreeDetails(card));
    });

    // Save button event listener
    document.getElementById('saveTreeName').addEventListener('click', () => {
        const newName = document.getElementById('treeDetailsTitle').value;
        const index = document.getElementById('treeDetailsCard').dataset.index;

        fetch('/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, index: parseInt(index) })
        })
        .then(response => response.ok ? window.location.reload() : console.error('Failed to save'))
        .catch(error => console.error('Error:', error));
    });

    // Increase or decrease the value by 10 on button clicks
    document.getElementById('incrementButton').addEventListener('click', function() {
        let waterInput = document.getElementById('waterInput');
        waterInput.value = parseInt(waterInput.value) + 10;
    });
    
    document.getElementById('decrementButton').addEventListener('click', function() {
        let waterInput = document.getElementById('waterInput');
        // Prevent the value from going below 0
        waterInput.value = Math.max(0, parseInt(waterInput.value) - 10);
    });
});