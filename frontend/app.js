
/* GLOBAL STATE */

let loadedDocuments = [];

let selectedDocumentId =
    localStorage.getItem(
        "doclensai_selected_document_id"
    ) || null;


/* UTILITY FUNCTIONS */

function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* RESET QUERY RESULTS */

function resetQueryResults() {

    const answerContainer =
        document.getElementById("answer");

    const sourcesContainer =
        document.getElementById("sources");

    const queryStatus =
        document.getElementById("queryStatus");


    answerContainer.innerHTML = `
        <div class="empty-state">

            <div class="empty-icon">
                AI
            </div>

            <p>
                Ask a question to generate
                an evidence-grounded answer.
            </p>

        </div>
    `;


    sourcesContainer.innerHTML = `
        <div class="empty-sources">
            Retrieved evidence will appear here.
        </div>
    `;


    queryStatus.textContent = "";

    queryStatus.className =
        "status-message";
}


/* RESET UPLOAD PANEL */

function resetUploadPanel() {

    const fileInput =
        document.getElementById(
            "fileInput"
        );

    const uploadStatus =
        document.getElementById(
            "uploadStatus"
        );

    const uploadArea =
        document.querySelector(
            ".upload-area"
        );


    if (fileInput) {

        fileInput.value =
            "";
    }


    if (uploadStatus) {

        uploadStatus.textContent =
            "";

        uploadStatus.className =
            "status-message";
    }


    if (uploadArea) {

        const uploadText =
            uploadArea.querySelector(
                "strong"
            );

        const uploadDescription =
            uploadArea.querySelector(
                "span"
            );


        if (uploadText) {

            uploadText.textContent =
                "Choose a PDF document";
        }


        if (uploadDescription) {

            uploadDescription.textContent =
                "Select a PDF to extract, chunk and index";
        }
    }
}


/* UPDATE DOCUMENT CARD SELECTION */

function updateDocumentCards() {

    const documentCards =
        document.querySelectorAll(
            ".document-card"
        );


    documentCards.forEach(
        function (card) {

            const cardDocumentId =
                card.dataset.documentId;


            if (
                cardDocumentId ===
                selectedDocumentId
            ) {

                card.classList.add(
                    "selected"
                );

            } else {

                card.classList.remove(
                    "selected"
                );
            }
        }
    );
}


/* SET SELECTED DOCUMENT */

function setSelectedDocument(
    documentId,
    clearResults = true
) {

    selectedDocumentId =
        documentId || null;


    if (selectedDocumentId) {

        localStorage.setItem(
            "doclensai_selected_document_id",
            selectedDocumentId
        );

    } else {

        localStorage.removeItem(
            "doclensai_selected_document_id"
        );
    }


    const documentSelect =
        document.getElementById(
            "documentSelect"
        );


    if (documentSelect) {

        documentSelect.value =
            selectedDocumentId || "";
    }


    updateDocumentCards();


    if (clearResults) {

        resetQueryResults();
    }
}


/* POPULATE DOCUMENT SELECTOR */

function populateDocumentSelect() {

    const documentSelect =
        document.getElementById(
            "documentSelect"
        );


    documentSelect.innerHTML = "";


    if (
        !loadedDocuments ||
        loadedDocuments.length === 0
    ) {

        const option =
            document.createElement(
                "option"
            );

        option.value = "";

        option.textContent =
            "No documents available";

        documentSelect.appendChild(
            option
        );

        documentSelect.disabled =
            true;

        selectedDocumentId =
            null;

        localStorage.removeItem(
            "doclensai_selected_document_id"
        );

        return;
    }


    documentSelect.disabled =
        false;


    loadedDocuments.forEach(
        function (doc) {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                doc.document_id;

            option.textContent =
                doc.filename;

            documentSelect.appendChild(
                option
            );
        }
    );


    const storedDocumentExists =
        loadedDocuments.some(
            function (doc) {

                return (
                    doc.document_id ===
                    selectedDocumentId
                );
            }
        );


    if (!storedDocumentExists) {

        selectedDocumentId =
            loadedDocuments[0]
                .document_id;

        localStorage.setItem(
            "doclensai_selected_document_id",
            selectedDocumentId
        );
    }


    documentSelect.value =
        selectedDocumentId;
}


/* RENDER DOCUMENT LIBRARY */

function renderDocumentLibrary() {

    const documentsContainer =
        document.getElementById(
            "documents"
        );


    documentsContainer.innerHTML = "";


    if (
        !loadedDocuments ||
        loadedDocuments.length === 0
    ) {

        documentsContainer.innerHTML = `
            <div class="empty-sources">
                No documents have been indexed yet.
            </div>
        `;

        return;
    }


    loadedDocuments.forEach(
        function (doc) {

            const documentElement =
                document.createElement(
                    "div"
                );


            documentElement.className =
                "document-card";


            documentElement.dataset.documentId =
                doc.document_id;


            documentElement.innerHTML = `

                <div class="document-info">

                    <div class="document-card-header">

                        <h3>
                            ${escapeHtml(doc.filename)}
                        </h3>

                        <button
                            type="button"
                            class="document-delete-button"
                            title="Delete document"
                            aria-label="Delete ${escapeHtml(doc.filename)}"
                        >
                            ×
                        </button>

                    </div>

                    <div class="document-meta">

                        <span class="page-count">
                            ${escapeHtml(doc.pages)}
                            pages
                        </span>

                        <span class="meta-dot">
                            ·
                        </span>

                        <span class="chunk-count">
                            ${escapeHtml(doc.chunks)}
                            chunks
                        </span>

                    </div>

                </div>
            `;


            const deleteButton =
                documentElement.querySelector(
                    ".document-delete-button"
                );


            deleteButton.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();


                    deleteDocument(
                        doc.document_id,
                        doc.filename
                    );
                }
            );


            documentElement.addEventListener(
                "click",
                function () {

                    setSelectedDocument(
                        doc.document_id
                    );
                }
            );


            documentsContainer.appendChild(
                documentElement
            );
        }
    );


    updateDocumentCards();
}


/* LOAD DOCUMENTS */

async function loadDocuments(
    preferredDocumentId = null
) {

    const documentsContainer =
        document.getElementById(
            "documents"
        );


    try {

        const response =
            await fetch(
                "/documents"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load documents."
            );
        }


        const data =
            await response.json();


        loadedDocuments =
            data.documents || [];


        if (
            preferredDocumentId &&
            loadedDocuments.some(
                function (doc) {

                    return (
                        doc.document_id ===
                        preferredDocumentId
                    );
                }
            )
        ) {

            selectedDocumentId =
                preferredDocumentId;

            localStorage.setItem(
                "doclensai_selected_document_id",
                preferredDocumentId
            );
        }


        populateDocumentSelect();

        renderDocumentLibrary();

    } catch (error) {

        documentsContainer.innerHTML = `
            <div class="empty-sources">
                Error: ${escapeHtml(error.message)}
            </div>
        `;


        const documentSelect =
            document.getElementById(
                "documentSelect"
            );


        documentSelect.innerHTML = `
            <option value="">
                Unable to load documents
            </option>
        `;


        documentSelect.disabled =
            true;
    }
}


/* CUSTOM DELETE CONFIRMATION MODAL */

function showDeleteConfirmation(filename) {

    return new Promise(
        function (resolve) {

            const existingModal =
                document.getElementById(
                    "deleteConfirmationModal"
                );


            if (existingModal) {

                existingModal.remove();
            }


            const modalOverlay =
                document.createElement(
                    "div"
                );


            modalOverlay.id =
                "deleteConfirmationModal";

            modalOverlay.className =
                "delete-modal-overlay";


            modalOverlay.innerHTML = `

                <div
                    class="delete-modal"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="deleteModalTitle"
                >

                    <div class="delete-modal-icon">
                        !
                    </div>


                    <h3 id="deleteModalTitle">
                        Delete Document?
                    </h3>


                    <div class="delete-modal-filename">
                        ${escapeHtml(filename)}
                    </div>


                    <p class="delete-modal-message">
                        This will permanently remove the PDF
                        and all of its indexed evidence.
                    </p>


                    <div class="delete-modal-actions">

                        <button
                            type="button"
                            class="delete-modal-cancel"
                        >
                            Cancel
                        </button>


                        <button
                            type="button"
                            class="delete-modal-confirm"
                        >
                            Delete
                        </button>

                    </div>

                </div>
            `;


            document.body.appendChild(
                modalOverlay
            );


            const cancelButton =
                modalOverlay.querySelector(
                    ".delete-modal-cancel"
                );


            const confirmButton =
                modalOverlay.querySelector(
                    ".delete-modal-confirm"
                );


            const closeModal =
                function (result) {

                    document.removeEventListener(
                        "keydown",
                        handleKeydown
                    );

                    modalOverlay.remove();

                    resolve(result);
                };


            const handleKeydown =
                function (event) {

                    if (
                        event.key ===
                        "Escape"
                    ) {

                        closeModal(
                            false
                        );
                    }
                };


            cancelButton.addEventListener(
                "click",
                function () {

                    closeModal(
                        false
                    );
                }
            );


            confirmButton.addEventListener(
                "click",
                function () {

                    closeModal(
                        true
                    );
                }
            );


            modalOverlay.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target ===
                        modalOverlay
                    ) {

                        closeModal(
                            false
                        );
                    }
                }
            );


            document.addEventListener(
                "keydown",
                handleKeydown
            );


            confirmButton.focus();
        }
    );
}


/* DELETE DOCUMENT */

async function deleteDocument(
    documentId,
    filename
) {

    const confirmed =
        await showDeleteConfirmation(
            filename
        );


    if (!confirmed) {

        return;
    }


    const deletedDocumentWasSelected =
        documentId ===
        selectedDocumentId;


    try {

        const response =
            await fetch(
                `/documents/${documentId}`,
                {
                    method:
                        "DELETE"
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch {

            data = {};
        }


        if (!response.ok) {

            const errorMessage =
                data.detail ||
                data.message ||
                "Failed to delete document.";


            throw new Error(
                errorMessage
            );
        }


        /* Reload the library and selector. */

        await loadDocuments();


        /* Clear any stale upload filename,
           duplicate warning or upload status. */

        resetUploadPanel();


        /* Clear answer and evidence if the
           deleted document was selected. */

        if (deletedDocumentWasSelected) {

            resetQueryResults();
        }


    } catch (error) {

        window.alert(
            "Delete failed: " +
            error.message
        );
    }
}


/* UPLOAD DOCUMENT */

async function uploadDocument() {

    const fileInput =
        document.getElementById(
            "fileInput"
        );

    const uploadButton =
        document.getElementById(
            "uploadButton"
        );

    const uploadStatus =
        document.getElementById(
            "uploadStatus"
        );


    const file =
        fileInput.files[0];


    if (!file) {

        uploadStatus.textContent =
            "Please choose a PDF document.";

        uploadStatus.className =
            "status-message error";

        return;
    }


    if (
        file.type !==
        "application/pdf"
    ) {

        uploadStatus.textContent =
            "Only PDF documents are supported.";

        uploadStatus.className =
            "status-message error";

        return;
    }


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    uploadButton.disabled =
        true;

    uploadButton.textContent =
        "Uploading & Indexing...";


    uploadStatus.textContent =
        "Processing document...";

    uploadStatus.className =
        "status-message";


    try {

        const response =
            await fetch(
                "/documents/upload",
                {
                    method:
                        "POST",

                    body:
                        formData
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch {

            data = {};
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Document upload failed."
            );
        }


        uploadStatus.textContent =
            "Document uploaded and indexed successfully.";

        uploadStatus.className =
            "status-message success";


        /* Clear actual file input. */

        fileInput.value =
            "";


        /* Restore the visible upload area. */

        const uploadArea =
            document.querySelector(
                ".upload-area"
            );


        if (uploadArea) {

            const uploadText =
                uploadArea.querySelector(
                    "strong"
                );

            const uploadDescription =
                uploadArea.querySelector(
                    "span"
                );


            if (uploadText) {

                uploadText.textContent =
                    "Choose a PDF document";
            }


            if (uploadDescription) {

                uploadDescription.textContent =
                    "Select a PDF to extract, chunk and index";
            }
        }


        /* Automatically select the document
           that was just uploaded. */

        const uploadedDocumentId =
            data.document_id ||
            null;


        await loadDocuments(
            uploadedDocumentId
        );


    } catch (error) {

        uploadStatus.textContent =
            error.message;

        uploadStatus.className =
            "status-message error";


    } finally {

        uploadButton.disabled =
            false;

        uploadButton.textContent =
            "Upload & Index";
    }
}


/* RENDER AI ANSWER */

function renderAnswer(answer) {

    const answerContainer =
        document.getElementById(
            "answer"
        );


    if (!answer) {

        answerContainer.innerHTML = `
            <div class="empty-state">

                <div class="empty-icon">
                    AI
                </div>

                <p>
                    No answer was generated.
                </p>

            </div>
        `;

        return;
    }


    answerContainer.innerHTML = `
        <div class="generated-answer">
            ${escapeHtml(answer)}
        </div>
    `;
}


/* RENDER EVIDENCE SOURCES */

function renderSources(sources) {

    const sourcesContainer =
        document.getElementById(
            "sources"
        );


    sourcesContainer.innerHTML =
        "";


    if (
        !sources ||
        sources.length === 0
    ) {

        sourcesContainer.innerHTML = `
            <div class="empty-sources">
                No evidence sources returned.
            </div>
        `;

        return;
    }


    sources.forEach(
        function (
            source,
            index
        ) {

            const sourceCard =
                document.createElement(
                    "div"
                );


            sourceCard.className =
                "source-card";


            sourceCard.innerHTML = `

                <h4>
                    Source ${index + 1}
                </h4>


                <p>
                    <strong>
                        Document:
                    </strong>

                    ${escapeHtml(source.filename)}
                </p>


                <p>
                    <strong>
                        Page:
                    </strong>

                    ${escapeHtml(source.page_number)}
                </p>


                <p>
                    <strong>
                        Chunk:
                    </strong>

                    ${escapeHtml(source.chunk_number)}
                </p>
            `;


            sourcesContainer.appendChild(
                sourceCard
            );
        }
    );
}


/* ASK QUESTION */

async function askQuestion() {

    const questionInput =
        document.getElementById(
            "question"
        );

    const topKInput =
        document.getElementById(
            "topK"
        );

    const askButton =
        document.getElementById(
            "askButton"
        );

    const queryStatus =
        document.getElementById(
            "queryStatus"
        );


    const question =
        questionInput.value.trim();


    if (!selectedDocumentId) {

        queryStatus.textContent =
            "Please select a document.";

        queryStatus.className =
            "status-message error";

        return;
    }


    if (!question) {

        queryStatus.textContent =
            "Please enter a question.";

        queryStatus.className =
            "status-message error";

        return;
    }


    const topK =
        Number(
            topKInput.value
        );


    askButton.disabled =
        true;

    askButton.textContent =
        "Generating Answer...";


    queryStatus.textContent =
        "Retrieving evidence and generating answer...";

    queryStatus.className =
        "status-message";


    try {

        const response =
            await fetch(
                "/query",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                question:
                                    question,

                                document_id:
                                    selectedDocumentId,

                                top_k:
                                    topK
                            }
                        )
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch {

            data = {};
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "Failed to generate answer."
            );
        }


        renderAnswer(
            data.answer
        );


        renderSources(
            data.sources
        );


        queryStatus.textContent =
            `Question answered successfully using up to ${topK} retrieved evidence chunks.`;

        queryStatus.className =
            "status-message success";


    } catch (error) {

        queryStatus.textContent =
            error.message;

        queryStatus.className =
            "status-message error";


        renderAnswer(
            null
        );


        renderSources(
            []
        );


    } finally {

        askButton.disabled =
            false;

        askButton.textContent =
            "Ask Question";
    }
}


/* FILE INPUT DISPLAY */

function updateFileSelection() {

    const fileInput =
        document.getElementById(
            "fileInput"
        );

    const uploadArea =
        document.querySelector(
            ".upload-area"
        );

    const uploadStatus =
        document.getElementById(
            "uploadStatus"
        );


    if (
        !uploadArea ||
        !fileInput.files ||
        fileInput.files.length === 0
    ) {

        return;
    }


    const selectedFile =
        fileInput.files[0];


    const uploadText =
        uploadArea.querySelector(
            "strong"
        );

    const uploadDescription =
        uploadArea.querySelector(
            "span"
        );


    if (uploadText) {

        uploadText.textContent =
            selectedFile.name;
    }


    if (uploadDescription) {

        uploadDescription.textContent =
            "PDF selected and ready to index";
    }


    /* A new file selection makes any previous
       upload error or status obsolete. */

    if (uploadStatus) {

        uploadStatus.textContent =
            "";

        uploadStatus.className =
            "status-message";
    }
}


/* DOCUMENT SELECT CHANGE */

function handleDocumentSelectChange(
    event
) {

    const documentId =
        event.target.value;


    if (!documentId) {

        setSelectedDocument(
            null
        );

        return;
    }


    setSelectedDocument(
        documentId
    );
}


/* INITIALIZE APPLICATION */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const uploadButton =
            document.getElementById(
                "uploadButton"
            );

        const askButton =
            document.getElementById(
                "askButton"
            );

        const fileInput =
            document.getElementById(
                "fileInput"
            );

        const documentSelect =
            document.getElementById(
                "documentSelect"
            );

        const questionInput =
            document.getElementById(
                "question"
            );


        uploadButton.addEventListener(
            "click",
            uploadDocument
        );


        askButton.addEventListener(
            "click",
            askQuestion
        );


        fileInput.addEventListener(
            "change",
            updateFileSelection
        );


        documentSelect.addEventListener(
            "change",
            handleDocumentSelectChange
        );


        questionInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.ctrlKey &&
                    event.key ===
                    "Enter"
                ) {

                    askQuestion();
                }
            }
        );


        loadDocuments();
    }
);