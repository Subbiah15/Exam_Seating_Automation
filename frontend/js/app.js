/* ===================================
   INTELLIGENT EXAM SEATING ENGINE
   Frontend JavaScript Application
   =================================== */

// Configuration
const API_BASE_URL = 'http://127.0.0.1:8081/api';
let currentPage = 'home-page';
let studentsData = [];
let hallsData = [];
let arrangementsData = [];
let currentArrangementId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing Exam Seating Engine UI...');
    
    // Setup navigation event listeners
    setupNavigation();
    
    // Load initial data
    loadStatistics();
    loadHalls();
    
    // Setup form event listeners
    setupFormListeners();
    // Ensure buttons have predictable IDs (HTML uses inline onclicks)
    attachUiButtonIds();
    // Capacity display on halls page
    setupCapacityDisplay();
    // Set today's date as default in exam date field
    setTodayDateDefault();
    
    // Show home page by default
    navigateTo('home');
    
    console.log('Application initialized successfully');
}

/**
 * Set today's date as default in exam date input
 */
function setTodayDateDefault() {
    const examDateInput = document.getElementById('examDate');
    if (examDateInput) {
        // Don't set a default date - let user choose
    }
}

/**
 * Setup navigation bar event listeners
 */
function setupNavigation() {
    // Navigation links are setup inline with onclick handlers
    // This function is here for future enhancements
    console.log('Navigation setup complete');
}

/**
 * Navigate to a specific page
 * @param {string} pageId - The page ID to navigate to
 */
function navigateTo(pageId) {
    // Convert short IDs to full IDs
    const pageMap = {
        'home': 'home-page',
        'upload': 'upload-page',
        'halls': 'halls-page',
        'generate': 'generate-page',
        'results': 'results-page',
        'help': 'help-page'
    };
    
    const fullPageId = pageMap[pageId] || pageId;
    
    // Hide all pages
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(fullPageId);
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = fullPageId;
    }
    
    // Update navbar
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Find and mark the active nav link (pageId may be short e.g. 'results' or full 'results-page')
    const shortId = fullPageId.replace('-page', '');
    const activeLink = document.querySelector(`.nav-link[href="#${shortId}"]`) || document.querySelector(`.nav-link[href="#${pageId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Load page-specific data
    loadStatistics(); // Always load statistics on every page
    
    if (fullPageId === 'results-page') {
        loadArrangements();
    } else if (fullPageId === 'halls-page') {
        loadHalls();
    } else if (fullPageId === 'generate-page') {
        loadHalls();
        loadSubjects();
        updateGeneratePrerequisiteAlert();
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
}

/**
 * Setup form event listeners
 */
function setupFormListeners() {
    // Note: primary buttons are wired via inline onclick in HTML.
    // We still wire refresh and modal download here.
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            if (currentArrangementId) downloadPDF(currentArrangementId);
        });
    }

    // View Seat Map button
    const viewSeatMapBtn = document.getElementById('viewSeatMapBtn');
    if (viewSeatMapBtn) {
        viewSeatMapBtn.addEventListener('click', () => {
            // Click the seat map tab to show it
            const seatMapTab = document.getElementById('seatMapTab');
            if (seatMapTab) {
                seatMapTab.click();
            }
        });
    }
    
    // Quick action buttons
    const quickUpload = document.querySelector('[data-action="upload"]');
    const quickGenerate = document.querySelector('[data-action="generate"]');
    const quickResults = document.querySelector('[data-action="results"]');
    
    if (quickUpload) quickUpload.addEventListener('click', () => navigateTo('upload-page'));
    if (quickGenerate) quickGenerate.addEventListener('click', () => navigateTo('generate-page'));
    if (quickResults) quickResults.addEventListener('click', () => navigateTo('results-page'));
}

/**
 * Attach predictable IDs to key UI buttons (so loading states work)
 */
function attachUiButtonIds() {
    const uploadBtn = document.querySelector('#uploadForm button[type="button"]');
    if (uploadBtn && !uploadBtn.id) uploadBtn.id = 'uploadStudentBtn';

    const addHallBtn = document.querySelector('#hallForm button');
    if (addHallBtn && !addHallBtn.id) addHallBtn.id = 'addHallBtn';

    const generateBtn = document.querySelector('#generateForm button[type="button"]');
    if (generateBtn && !generateBtn.id) generateBtn.id = 'generateSeatingBtn';

    const refreshBtn = document.querySelector('#results-page .fa-sync')?.closest('button');
    if (refreshBtn && !refreshBtn.id) refreshBtn.id = 'refreshArrangementsBtn';
}

/**
 * Update capacity display when rows/columns change on halls form
 */
function setupCapacityDisplay() {
    const rowsInput = document.getElementById('rows');
    const colsInput = document.getElementById('columns');
    const displayEl = document.getElementById('capacityDisplay');
    if (!displayEl) return;
    function update() {
        const r = parseInt(rowsInput?.value, 10) || 0;
        const c = parseInt(colsInput?.value, 10) || 0;
        displayEl.textContent = (r * c).toString();
    }
    if (rowsInput) rowsInput.addEventListener('input', update);
    if (colsInput) colsInput.addEventListener('input', update);
    update();
}

/**
 * Load and display statistics
 */
async function loadStatistics() {
    try {
        const [studentsRes, hallsRes, arrangementsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/students/count`),
            fetch(`${API_BASE_URL}/halls`),
            fetch(`${API_BASE_URL}/seating/arrangements`)
        ]);
        
        const studentsCount = studentsRes.ok ? await studentsRes.json() : { count: 0 };
        const hallsResponse = hallsRes.ok ? await hallsRes.json() : { halls: [] };
        const arrangementsResponse = arrangementsRes.ok ? await arrangementsRes.json() : { arrangements: [] };
        
        // Update statistics (match HTML IDs)
        const statStudents = document.getElementById('stat-students');
        const statHalls = document.getElementById('stat-halls');
        const statArr = document.getElementById('stat-arrangements');
        const statUtil = document.getElementById('stat-utilization');
        if (statStudents) statStudents.textContent = (studentsCount.count || 0).toString();
        if (statHalls) statHalls.textContent = (hallsResponse.halls?.length || 0).toString();
        if (statArr) statArr.textContent = (arrangementsResponse.arrangements?.length || 0).toString();
        const arrs = arrangementsResponse.arrangements || [];
        const avgUtil = arrs.length > 0
            ? (arrs.reduce((sum, a) => sum + (Number(a.utilization) || 0), 0) / arrs.length).toFixed(1)
            : 0;
        if (statUtil) statUtil.textContent = avgUtil + '%';

        updateGeneratePrerequisiteAlert();
    } catch (error) {
        console.error('Error loading statistics:', error);
        showAlert('Error loading statistics', 'danger');
    }
}

/**
 * Update a statistic card value
 * @param {string} cardId - The card ID
 * @param {number} value - The value to display
 */
function updateStatisticCard(cardId, value) {
    const card = document.querySelector(`[data-stat="${cardId}"]`);
    if (card) {
        card.textContent = value;
    }
}

/**
 * Upload student file
 */
async function uploadStudentFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
        showAlert('Please upload a CSV or Excel file', 'danger');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoadingState('uploadStudentBtn', true);
        
        const response = await fetch(`${API_BASE_URL}/seating/upload-students`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showAlert(`Successfully uploaded ${result.count} students`, 'success');
            fileInput.value = '';
            
            // Refresh statistics
            loadStatistics();
            
            // Add to recent uploads table
            addRecentUpload(file.name, result.count);
        } else {
            const error = await response.json();
            showAlert(`Upload failed: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('Error uploading file', 'danger');
    } finally {
        showLoadingState('uploadStudentBtn', false);
    }
}

/**
 * Add recent upload to table
 * @param {string} fileName - The file name
 * @param {number} count - Number of students uploaded
 */
function addRecentUpload(fileName, count) {
    const container = document.getElementById('recentUploads');
    if (!container) return;

    let tableBody = document.querySelector('#recentUploadsTable tbody');
    if (!tableBody) {
        container.innerHTML = `
            <table class="table table-sm">
                <thead><tr><th>File</th><th>Count</th><th>Time</th><th>Status</th></tr></thead>
                <tbody id="recentUploadsTableBody"></tbody>
            </table>
        `;
        tableBody = document.getElementById('recentUploadsTableBody');
    }

    const row = document.createElement('tr');
    const now = new Date().toLocaleString();
    row.innerHTML = `
        <td>${fileName}</td>
        <td><span class="badge bg-success">${count} students</span></td>
        <td>${now}</td>
        <td><span class="badge bg-primary">Processed</span></td>
    `;
    tableBody.insertBefore(row, tableBody.firstChild);

    while (tableBody.children.length > 5) {
        tableBody.removeChild(tableBody.lastChild);
    }
}

/**
 * Add a new exam hall
 */
async function addHall() {
    const nameInput = document.getElementById('hallName');
    const rowsInput = document.getElementById('rows');
    const colsInput = document.getElementById('columns');
    const locationInput = document.getElementById('location');
    const name = nameInput.value.trim();
    const rows = parseInt(rowsInput.value);
    const cols = parseInt(colsInput.value);
    const seats = rows * cols;
    
    // Validation
    if (!name) {
        showAlert('Hall name is required', 'warning');
        return;
    }
    
    if (isNaN(seats) || seats <= 0) {
        showAlert('Total seats must be a positive number', 'warning');
        return;
    }
    
    if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
        showAlert('Rows and columns must be positive numbers', 'warning');
        return;
    }
    
    if (rows * cols !== seats) {
        showAlert('Rows × Columns must equal Total Seats', 'danger');
        return;
    }
    
    try {
        showLoadingState('addHallBtn', true);
        
        const response = await fetch(`${API_BASE_URL}/halls/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                total_seats: seats,
                rows: rows,
                columns: cols
            })
        });
        
        if (response.ok) {
            showAlert('Hall added successfully', 'success');
            
            // Clear form
            nameInput.value = '';
            rowsInput.value = '';
            colsInput.value = '';
            if (locationInput) locationInput.value = '';
            
            // Refresh halls list
            loadHalls();
            loadStatistics();
        } else {
            const error = await response.json();
            showAlert(`Error: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Error adding hall:', error);
        showAlert('Error adding hall', 'danger');
    } finally {
        showLoadingState('addHallBtn', false);
    }
}

/**
 * Load and display exam halls
 */
async function loadHalls() {
    try {
        const response = await fetch(`${API_BASE_URL}/halls`);
        
        if (response.ok) {
            const data = await response.json();
            hallsData = data.halls || [];
            
            // Update halls list display
            displayHallsList();
            
            // Update halls select for generate page
            updateHallsSelect();
            updateGeneratePrerequisiteAlert();
        }
    } catch (error) {
        console.error('Error loading halls:', error);
        showAlert('Error loading halls', 'danger');
    }
}

/**
 * Display halls in the table
 */
function displayHallsList() {
    const container = document.getElementById('hallsList');
    if (!container) return;
    
    if (hallsData.length === 0) {
        container.innerHTML = '<p class="text-muted">No halls added yet</p>';
        return;
    }

    let html = '<div class="list-group">';
    hallsData.forEach(hall => {
        html += `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${hall.name}</h6>
                    <small class="text-muted">${hall.rows} × ${hall.columns} &middot; ${hall.total_seats} seats</small>
                </div>
                <div>
                    <button class="btn btn-sm btn-info me-2" onclick="editHall('${hall.id}')"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-danger" onclick="deleteHall('${hall.id}')"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Show or hide prerequisite alert on Generate page
 */
function updateGeneratePrerequisiteAlert() {
    const alertEl = document.getElementById('prerequisiteAlert');
    if (!alertEl) return;
    const hasStudents = (document.getElementById('stat-students')?.textContent || '0') !== '0';
    const hasHalls = hallsData.length > 0;
    if (hasStudents && hasHalls) {
        alertEl.classList.add('d-none');
    } else {
        alertEl.classList.remove('d-none');
    }
}

/**
 * Update halls select options
 */
function updateHallsSelect() {
    const checkboxContainer = document.getElementById('hallsCheckbox');
    if (!checkboxContainer) return;
    
    checkboxContainer.innerHTML = '';
    
    if (hallsData.length === 0) {
        checkboxContainer.innerHTML = '<p class="text-muted">No halls available. Please add halls first.</p>';
        return;
    }
    
    hallsData.forEach(hall => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        checkDiv.innerHTML = `
            <input class="form-check-input" type="checkbox" id="hall_${hall.id}" value="${hall.id}" data-hall-name="${hall.name}">
            <label class="form-check-label" for="hall_${hall.id}">
                ${hall.name} (${hall.total_seats} seats)
            </label>
        `;
        
        checkboxContainer.appendChild(checkDiv);
    });
}

/**
 * Load available subjects from uploaded students
 */
async function loadSubjects() {
    try {
        const response = await fetch(`${API_BASE_URL}/students/subjects`);
        if (!response.ok) {
            console.log('Subjects endpoint not available yet');
            return;
        }
        
        const data = await response.json();
        updateSubjectsCheckbox(data.subject_details || []);
    } catch (e) {
        console.error('Error loading subjects:', e);
    }
}

/**
 * Update subjects checkbox display
 */
function updateSubjectsCheckbox(subjectDetails) {
    const checkboxContainer = document.getElementById('subjectsCheckbox');
    if (!checkboxContainer) return;
    
    checkboxContainer.innerHTML = '';
    
    if (subjectDetails.length === 0) {
        checkboxContainer.innerHTML = '<p class="text-muted">No subjects available. Please upload students first.</p>';
        return;
    }
    
    subjectDetails.forEach(subject => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'form-check';
        
        checkDiv.innerHTML = `
            <input class="form-check-input" type="checkbox" id="subject_${subject.code}" value="${subject.code}" data-subject-code="${subject.code}">
            <label class="form-check-label" for="subject_${subject.code}">
                ${subject.code} (${subject.count} students)
            </label>
        `;
        
        checkboxContainer.appendChild(checkDiv);
    });
}

/**
 * Generate seating arrangement for selected date and subjects
 */
async function generateSeating() {
    const examDateInput = document.getElementById('examDate');
    const examDate = examDateInput ? examDateInput.value : '';
    
    // Get selected subjects
    const selectedSubjectCheckboxes = document.querySelectorAll('#subjectsCheckbox input[type="checkbox"]:checked');
    const selectedSubjects = Array.from(selectedSubjectCheckboxes).map(cb => cb.value);
    
    // Get selected halls
    const selectedHallCheckboxes = document.querySelectorAll('#hallsCheckbox input[type="checkbox"]:checked');
    const selectedHallIds = Array.from(selectedHallCheckboxes).map(cb => cb.value);
    
    // Validation
    if (!examDate) {
        showAlert('Please select an exam date', 'warning');
        return;
    }
    
    if (selectedSubjects.length === 0) {
        showAlert('Please select at least one subject', 'warning');
        return;
    }
    
    if (selectedHallIds.length === 0) {
        showAlert('Please select at least one hall', 'warning');
        return;
    }
    
    try {
        showLoadingState('generateSeatingBtn', true);
        
        const response = await fetch(`${API_BASE_URL}/seating/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                exam_date: examDate,
                subject_codes: selectedSubjects,
                hall_ids: selectedHallIds,
                algorithm: 'greedy'
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            showAlert(
                `Success! Generated seating for ${selectedSubjects.join(', ')} on ${examDate}. 
                 Assigned: ${result.assigned}/${result.total_students} students, 
                 Conflicts: ${result.conflicts}`,
                'success'
            );
            
            // Refresh arrangements
            loadArrangements();
            loadStatistics();
            
            // Navigate to results
            setTimeout(() => navigateTo('results'), 1500);
        } else {
            const error = await response.json();
            showAlert(`Generation failed: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Generation error:', error);
        showAlert('Error generating seating arrangement', 'danger');
    } finally {
        showLoadingState('generateSeatingBtn', false);
    }
}

/**
 * Display arrangements in the table
 */
function displayArrangements() {
    const tableBody = document.getElementById('arrangementsTableBody');
    if (!tableBody) return;
    
    if (!arrangementsData || arrangementsData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No arrangements yet. Generate one from the Generate page.</td></tr>';
        return;
    }
    
    let html = '';
    arrangementsData.forEach(arr => {
        const successRate = ((arr.total_assigned / Math.max(1, arr.total_students)) * 100).toFixed(1);
        const statusBadge = successRate >= 95 ? 'success' : successRate >= 80 ? 'warning' : 'danger';
        const dateStr = arr.created_at ? new Date(arr.created_at).toLocaleDateString() : 'N/A';
        
        html += `
            <tr>
                <td>${arr.id || 'N/A'}</td>
                <td>${arr.exam_name || 'Unnamed'}</td>
                <td>${arr.total_assigned || 0}</td>
                <td>${(arr.utilization || 0).toFixed(1)}%</td>
                <td><span class="badge bg-${statusBadge}">${successRate}%</span></td>
                <td>${dateStr}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewSeatingDetails('${arr.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-success" onclick="downloadArrangement('${arr.id}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

/**
 * Load seating arrangements (fetches from API and renders table)
 */
async function loadArrangements() {
    try {
        const response = await fetch(`${API_BASE_URL}/seating/arrangements`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        arrangementsData = data.arrangements || [];
        
        // Display the arrangements in the table
        displayArrangements();
        loadStatistics();
    } catch (e) {
        console.error('Error fetching arrangements:', e);
        arrangementsData = [];
        // Display error in table
        const tableBody = document.getElementById('arrangementsTableBody');
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Failed to load arrangements. Please refresh the page.</td></tr>`;
        }
    }
}

/**
 * Refresh arrangements list (re-fetch and re-render)
 */
function refreshArrangements() {
    loadArrangements();
}

/**
 * View seating details
 * @param {string} arrangementId - The arrangement ID
 */
async function viewSeatingDetails(arrangementId) {
    try {
        const response = await fetch(`${API_BASE_URL}/seating/arrangement/${arrangementId}`);
        
        if (response.ok) {
            const data = await response.json();
            currentArrangementId = arrangementId;

            const titleEl = document.getElementById('seatingDetailTitle');
            const contentEl = document.getElementById('seatingDetailContent');
            if (titleEl) titleEl.textContent = `Seating: ${data.hall_name || 'All Halls'}`;
            let html = `
                <p><strong>Arrangement ID:</strong> ${data.id}</p>
                <p><strong>Hall(s):</strong> ${data.hall_name || 'All Halls'}</p>
                <p><strong>Exam Date:</strong> ${data.exam_date || 'N/A'}</p>
                <p><strong>Subjects:</strong> ${Array.isArray(data.subjects) ? data.subjects.join(', ') : data.subjects || 'N/A'}</p>
                <p><strong>Total Assigned:</strong> ${data.total_assigned || 0} / ${data.total_students || 0}</p>
                <p><strong>Success Rate:</strong> ${data.success_rate || 'N/A'}</p>
                <p><strong>Constraints Satisfied:</strong> ${data.constraints_satisfied ? 'Yes' : 'No'}</p>
            `;
            if (data.seats_data && data.seats_data.length > 0) {
                html += '<h6 class="mt-3">Seat Assignments (preview)</h6><div class="table-responsive"><table class="table table-sm table-bordered"><thead><tr><th>Hall</th><th>Row</th><th>Col</th><th>Student ID</th><th>Name</th><th>Subject</th></tr></thead><tbody>';
                data.seats_data.forEach(s => {
                    html += `<tr><td>${s.hall}</td><td>${s.row}</td><td>${s.column}</td><td>${s.student_id}</td><td>${s.student_name}</td><td>${s.student_subject || ''}</td></tr>`;
                });
                html += '</tbody></table></div>';
            }
            if (contentEl) contentEl.innerHTML = html;

            // Load seat map image
            loadSeatMapImage(arrangementId);

            const modalEl = document.getElementById('seatingDetailModal');
            if (modalEl && typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            }
        } else {
            showAlert('Error loading arrangement details', 'danger');
        }
    } catch (error) {
        console.error('Error fetching arrangement:', error);
        showAlert('Error loading arrangement details', 'danger');
    }
}


/**
 * Load and display seat map image from the backend
 * @param {string} arrangementId
 */
async function loadSeatMapImage(arrangementId) {
    try {
        const container = document.getElementById('seatMapContainer');
        if (!container) return;

        const seatMapUrl = `${API_BASE_URL}/seating/arrangement/${arrangementId}/seat-map`;
        
        // Create image element
        const img = document.createElement('img');
        img.src = seatMapUrl;
        img.alt = 'Seat Map';
        img.className = 'img-fluid';
        img.style.maxWidth = '100%';
        img.style.border = '1px solid #ddd';
        img.style.padding = '10px';
        img.style.borderRadius = '5px';
        img.style.marginTop = '10px';
        
        // Handle loading and errors
        img.onload = function() {
            container.innerHTML = '';
            container.appendChild(img);
        };
        
        img.onerror = function() {
            container.innerHTML = '<p class="text-danger"><i class="fas fa-exclamation-circle"></i> Failed to load seat map</p>';
        };
    } catch (error) {
        console.error('Error loading seat map:', error);
        const container = document.getElementById('seatMapContainer');
        if (container) {
            container.innerHTML = '<p class="text-danger">Error loading seat map</p>';
        }
    }
}


/**
 * Download arrangement (wrapper) - opens generated PDF/text in new tab
 * @param {string} arrangementId
 */
function downloadArrangement(arrangementId) {
    // Prefer opening the /pdf endpoint in a new tab for instant viewing
    const url = `${API_BASE_URL}/seating/arrangement/${arrangementId}/pdf`;
    // Open in new tab (browser will handle content-disposition)
    window.open(url, '_blank');
}

/**
 * Download seating as PDF
 * @param {string} arrangementId - The arrangement ID
 */
async function downloadPDF(arrangementId) {
    try {
        showLoadingState('downloadPdfBtn', true);
        
        const response = await fetch(`${API_BASE_URL}/seating/arrangement/${arrangementId}/pdf`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `seating-arrangement-${arrangementId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('PDF downloaded successfully', 'success');
        } else {
            showAlert('Error downloading PDF', 'danger');
        }
    } catch (error) {
        console.error('PDF download error:', error);
        showAlert('Error downloading PDF', 'danger');
    } finally {
        showLoadingState('downloadPdfBtn', false);
    }
}

/**
 * Edit hall
 * @param {string} hallId - The hall ID
 */
function editHall(hallId) {
    showAlert('To modify a hall, please delete it and create a new one with updated details', 'info');
}

/**
 * Delete hall
 * @param {string} hallId - The hall ID
 */
async function deleteHall(hallId) {
    if (!confirm('Are you sure you want to delete this hall?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/halls/${hallId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Hall deleted successfully', 'success');
            loadHalls();
            loadStatistics();
        } else {
            showAlert('Error deleting hall', 'danger');
        }
    } catch (error) {
        console.error('Error deleting hall:', error);
        showAlert('Error deleting hall', 'danger');
    }
}

/**
 * Show alert notification
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertId = 'alert_' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 
                          type === 'danger' ? 'exclamation-circle' : 
                          type === 'warning' ? 'warning' : 
                          'info-circle'}"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Show/hide loading state on button
 * @param {string} buttonId - The button ID
 * @param {boolean} isLoading - Whether to show loading state
 */
function showLoadingState(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span class="ms-2">Processing...</span>
        `;
    } else {
        button.disabled = false;
        // Restore original text based on button
        if (buttonId === 'uploadStudentBtn') {
            button.innerHTML = '<i class="fas fa-upload"></i> Upload Students';
        } else if (buttonId === 'addHallBtn') {
            button.innerHTML = '<i class="fas fa-plus"></i> Add Hall';
        } else if (buttonId === 'generateSeatingBtn') {
            button.innerHTML = '<i class="fas fa-cog"></i> Generate Seating';
        } else if (buttonId === 'downloadPdfBtn') {
            button.innerHTML = '<i class="fas fa-download"></i> Download PDF';
        }
    }
}

/**
 * Download template CSV
 */
function downloadTemplate() {
    const csvContent = `Student ID,Name,Enrollment No,Department,Subject
S001,John Doe,12345001,CSE,Database Systems
S002,Jane Smith,12345002,CSE,Data Structures
S003,Mike Johnson,12345003,ECE,Digital Circuits
S004,Sarah Wilson,12345004,ECE,Signals & Systems`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'students_template.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Export functions for global access
window.navigateTo = navigateTo;
window.uploadStudentFile = uploadStudentFile;
window.addHall = addHall;
window.generateSeating = generateSeating;
window.viewSeatingDetails = viewSeatingDetails;
window.loadSeatMapImage = loadSeatMapImage;
window.downloadPDF = downloadPDF;
window.downloadTemplate = downloadTemplate;
window.editHall = editHall;
window.deleteHall = deleteHall;
window.showAlert = showAlert;
window.refreshArrangements = refreshArrangements;