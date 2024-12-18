document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeFile');
    const selectedFileDiv = document.getElementById('selectedFile');
    const downloadBtn = document.getElementById('downloadBtn');

    // File Drop Zone functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFileSelect();
    }

    // File selection handling
    fileInput.addEventListener('change', handleFileSelect);

    function handleFileSelect() {
        const file = fileInput.files[0];
        if (file) {
            const fileName = document.querySelector('.selected-file .file-name');
            selectedFileDiv.classList.remove('hidden');
            fileName.textContent = file.name;
            submitBtn.disabled = false;
        }
    }

    // Remove file button
    document.querySelector('.remove-file').addEventListener('click', () => {
        fileInput.value = '';
        selectedFileDiv.classList.add('hidden');
        submitBtn.disabled = true;
    });

    // Form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file');
            return;
        }

        // Get selected options
        const selectedOptions = Array.from(document.querySelectorAll('input[name="extractOptions"]:checked'))
            .map(checkbox => checkbox.value);

        if (selectedOptions.length === 0) {
            alert('Please select at least one type of information to extract');
            return;
        }

        // Update UI for processing state
        submitBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('options', JSON.stringify(selectedOptions));
        
        try {
            const response = await fetch('/parse-resume/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                // Store the results in sessionStorage
                sessionStorage.setItem('resumeResults', JSON.stringify(data));
                displayResults(data);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to parse resume');
            }
        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
            loadingDiv.classList.add('hidden');
        }
    });

    function updateLoadingMessage(message) {
        const processingText = loadingDiv.querySelector('.processing-text');
        processingText.textContent = message;
    }

    function showError(message) {
        alert(`Error: ${message}`);
    }

    function displayResults(data) {
        try {
            // Format personal info
            const personalInfo = data.personal_info || {};
            const formattedPersonalInfo = Object.entries(personalInfo)
                .map(([key, value]) => `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}`)
                .join('\n');
            document.getElementById('personalInfo').textContent = formattedPersonalInfo || 'No personal information found';

            // Format contact info
            const contactInfo = data.contact_info || {};
            const formattedContactInfo = Object.entries(contactInfo)
                .map(([key, value]) => `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value || 'Not found'}`)
                .join('\n');
            document.getElementById('contactInfo').textContent = formattedContactInfo || 'No contact information found';

            // Display other sections
            document.getElementById('education').textContent = data.education || 'No education information found';
            document.getElementById('experience').textContent = data.experience || 'No experience information found';
            document.getElementById('skills').textContent = data.skills || 'No skills information found';
            document.getElementById('summary').textContent = data.summary || 'No summary available';

            // Show results and scroll
            loadingDiv.classList.add('hidden');
            resultsDiv.classList.remove('hidden');
            resultsDiv.scrollIntoView({ behavior: 'smooth' });

            // Log the displayed data for debugging
            console.log('Displayed data:', {
                personalInfo: formattedPersonalInfo,
                contactInfo: formattedContactInfo,
                education: data.education,
                experience: data.experience,
                skills: data.skills,
                summary: data.summary
            });
        } catch (error) {
            console.error('Error displaying results:', error);
            showError('Error displaying results. Please check the console for details.');
        }
    }

    // Download functionality
    downloadBtn.addEventListener('click', () => {
        const results = {};
        Object.keys(data).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                results[key] = element.textContent;
            }
        });

        const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume-analysis.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Add function to load stored results
    function loadStoredResults() {
        const storedResults = sessionStorage.getItem('resumeResults');
        if (storedResults) {
            const data = JSON.parse(storedResults);
            displayResults(data);
        }
    }

    // Call on page load
    document.addEventListener('DOMContentLoaded', loadStoredResults);
}); 