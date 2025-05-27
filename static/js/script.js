const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const fileInfo = document.getElementById('fileInfo');
const submitBtn = document.getElementById('submitBtn');
const form = document.getElementById('uploadForm');
const privacyInfoBtns = document.querySelectorAll('.privacyInfoBtn')
const modal = document.getElementById('privacyInfoModal');
const closeBtn = modal.querySelector('.modal-close');

uploadBtn.addEventListener('click', () => fileInput.click());

function isPDF(file) {
    return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
}

function showError(message) {
    fileInfo.innerHTML = `<p style="color: #e74c3c;">${message}</p>`;
    submitBtn.style.display = 'none';
}

function updateFileInfo(fileName, isPDFFile) {
    if (isPDFFile) {
        fileInfo.innerHTML = `<p>File selezionato: <strong>${fileName}</strong>
        <span class="remove-file" onclick="removeFile()" style="cursor:pointer;margin-left:0.5rem;">Rimuovi️</span></p>`;
        submitBtn.style.display = 'block';
    } else {
        showError('Errore: il file selezionato non è un PDF!');
    }
}

function removeFile() {
    fileInput.value = '';
    fileInfo.innerHTML = '';
    submitBtn.style.display = 'none';
}

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        updateFileInfo(file.name, isPDF(file));
    }
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    dropArea.classList.add('highlight');
}

function unhighlight() {
    dropArea.classList.remove('highlight');
}

dropArea.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    if (file) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        updateFileInfo(file.name, isPDF(file));
    }
});

form.addEventListener('submit', function (e) {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file || !isPDF(file)) {
        showError('Seleziona un file PDF valido prima di inviare.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Errore durante l’upload');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'processed_files.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        fileInfo.innerHTML = 'File processato correttamente.';
    })
    .catch(error => {
        console.error(error);
        showError('Errore durante il caricamento del file.');
    });
});

function showModal() {
  modal.classList.remove('hide');
  modal.classList.add('show');
}

function hideModal() {
  modal.classList.remove('show');
  modal.classList.add('hide');

  setTimeout(() => {
    modal.classList.remove('hide');
    modal.style.display = 'none';
  }, 300);
}

privacyInfoBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    modal.style.display = 'block';
    void modal.offsetWidth;
    showModal();
  });
});


closeBtn.addEventListener('click', hideModal);

window.addEventListener('click', (e) => {
  if (e.target === modal) {
    hideModal();
  }
});

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    hideModal();
  }
});
