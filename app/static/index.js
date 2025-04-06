function showTreeDetails(element) {


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