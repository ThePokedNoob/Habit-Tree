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

function completeHabit(habitName) {
    // Using fetch to send a POST request
    fetch('/complete_habit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit_name: habitName })
    })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                console.log(response);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Initialize Bootstrap Tooltips
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-tree]').forEach(card => {
        card.addEventListener('click', () => showTreeDetails(card));
    });

    // Save button event listener
    document.getElementById('saveTreeName').addEventListener('click', () => {
        const newName = document.getElementById('treeDetailsTitle').value;
        const index = document.getElementById('treeDetailsCard').dataset.index;

        fetch('/edit_tree', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, index: parseInt(index) })
        })
            .then(response => response.ok ? window.location.reload() : console.error('Failed to save'))
            .catch(error => console.error('Error:', error));
    });

    // Increase or decrease the value by 10 on button clicks
    document.getElementById('incrementButton').addEventListener('click', function () {
        let waterInput = document.getElementById('waterInput');
        waterInput.value = parseInt(waterInput.value) + 10;
    });

    document.getElementById('decrementButton').addEventListener('click', function () {
        let waterInput = document.getElementById('waterInput');
        // Prevent the value from going below 0
        waterInput.value = Math.max(0, parseInt(waterInput.value) - 10);
    })

    // Add Water button listener
    document.getElementById('confirmWaterButton').addEventListener('click', () => {
        const index = document.getElementById('treeDetailsCard').dataset.index;
        const water_amount = document.getElementById('waterInput').value;
        const errorText = document.getElementById('addWaterErrorText');

        // Clear previous error messages
        errorText.textContent = '';

        fetch('/water_tree', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ water_amount: water_amount, index: parseInt(index) })
        })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    // Try to parse JSON error response
                    response.json().then(data => {
                        errorText.textContent = data.error || 'Failed to water tree. Please try again.';
                    }).catch(() => {
                        errorText.textContent = 'An unexpected error occurred.';
                    });
                }
            })
            .catch(error => {
                errorText.textContent = 'Network error. Please check your connection.';
                console.error('Error:', error);
            });
    });

    // Update the add habit modal text based on which button triggered the modal.
    const habitModal = document.getElementById("habitModal");

    habitModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const action = button.getAttribute("data-action");

        const modalTitle = habitModal.querySelector(".modal-title");
        const confirmButton = habitModal.querySelector("#confirmButton");

        const habitNameInput = document.getElementById('habitName');
        const habitPriorityInput = document.getElementById('habitPriority');
        const dayIds = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

        if (action === "edit") {
            modalTitle.textContent = "Edit Habit";
            confirmButton.textContent = "Confirm Edit";
            confirmButton.dataset.action = "edit";

            // Get habit details from data attributes of the button.
            var habitName = button.getAttribute('data-habit-name') ;
            var habitPriority = button.getAttribute('data-habit-priority');
            const habitDaysStr = button.getAttribute("data-habit-days");
            const habitDays = habitDaysStr.split(",").map(day => day.trim());
            confirmButton.dataset.existingHabitName = habitName;

            // Pre-fill the input fields.
            habitNameInput.value = habitName || '';
            habitPriorityInput.value = habitPriority || 0;
            dayIds.forEach(function (day) {
                const checkbox = document.getElementById(day);
                if (checkbox) {
                    checkbox.checked = habitDays.includes(day);
                }
            });
        } else {
            modalTitle.textContent = "Add Habit";
            confirmButton.textContent = "Add Habit";
            confirmButton.dataset.action = "add";

            // Clear all input values.
            habitModal.querySelector("form").reset();
        }
    });

    // Add click event listener to the confirm button of adding/editing habit
    const confirmButton = document.getElementById("confirmButton");
    confirmButton.addEventListener("click", function () {
        // Determine the action (edit or add)
        const action = confirmButton.dataset.action;
        const habitNameElem = document.getElementById('habitName');
        const habitPriorityElem = document.getElementById('habitPriority');
        const errorText = document.getElementById('addHabitErrorText');

        // Get all checked day checkboxes and convert their ids to a proper day name.
        const selectedDays = Array.from(document.querySelectorAll("input.btn-check:checked"))
            .map(checkbox => {
                // Convert "monday" to "Monday", "tuesday" to "Tuesday", etc.
                return checkbox.id.charAt(0).toUpperCase() + checkbox.id.slice(1);
            });

        // Join selected days into a CSV string.
        const daysCSV = selectedDays.join(',');

        // Based on the action, handle accordingly.
        if (action === "edit") {
            // Create the data object to send via POST.
            const data = {
                existing_habit_name: confirmButton.dataset.existingHabitName,
                new_habit_name: habitNameElem.value,
                habit_priority: habitPriorityElem.value,
                days_of_the_week: daysCSV
            };

            fetch('/edit_habit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => {
                    if (response.ok) {
                        console.log('Success:', response);
                        window.location.reload()
                    } else {
                        // Try to parse JSON error response
                        response.json().then(data => {
                            errorText.textContent = data.error || 'Failed to add habit. Please try again.';
                        }).catch(() => {
                            errorText.textContent = 'An unexpected error occurred.';
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        } else if (action === "add") {
            // Create the data object to send via POST.
            const data = {
                habit_name: habitNameElem.value,
                habit_priority: habitPriorityElem.value,
                days_of_the_week: daysCSV // or send the array directly if your API is set up to handle it
            };

            // POST the data to your Flask API endpoint.
            fetch('/add_habit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => {
                    if (response.ok) {
                        console.log('Success:', response);
                        window.location.reload()
                    } else {
                        // Try to parse JSON error response
                        response.json().then(data => {
                            errorText.textContent = data.error || 'Failed to add habit. Please try again.';
                        }).catch(() => {
                            errorText.textContent = 'An unexpected error occurred.';
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    });
});