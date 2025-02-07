// Javascript setup for index.html

// Fetch available translations, books, and chapters dynamically
async function fetchTranslations() {
    const response = await fetch('/translations');
    const translations = await response.json();
    const translationSelect = document.getElementById('translation');
    translations.forEach((translation) => {
        const option = document.createElement('option');
        option.value = translation.identifier;  // Use the identifier as the value
        option.textContent = translation.name;  // Use the name as the displayed text
        translationSelect.appendChild(option);
    });
}

async function fetchBooks(translation) {
    const response = await fetch(`/books?translation=${translation}`);
    const books = await response.json();
    const bookSelect = document.getElementById('book');
    bookSelect.innerHTML = '<option value="" disabled selected>Select a book</option>';
    books.forEach((book) => {
        const option = document.createElement('option');
        option.value = book;  // Use the book name as the value
        option.textContent = book;  // Display the book name
        bookSelect.appendChild(option);
    });
}

async function fetchChapters(book, translation) {
    const response = await fetch(`/chapters?book=${book}&translation=${translation}`);
    const chapters = await response.json();

    const chapterSelect = document.getElementById('chapter');
    chapterSelect.innerHTML = '<option value="" disabled selected>Select a chapter</option>';

    if (Array.isArray(chapters) && chapters.length > 0) {
        chapters.forEach((chapterString) => {
            const option = document.createElement('option');
            option.value = chapterString;
            option.textContent = `Chapter ${chapterString}`;
            chapterSelect.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.textContent = "No chapters available";
        chapterSelect.appendChild(option);
    }
}


// Load the translation options when the page loads
window.onload = fetchTranslations;

// Event listener to fetch books based on selected translation
document.getElementById('translation').addEventListener('change', (event) => {
    const translation = event.target.value;
    fetchBooks(translation);
});

// Event listener to fetch chapters based on selected book and translation
document.getElementById('book').addEventListener('change', (event) => {
    const book = event.target.value;
    const translation = document.getElementById('translation').value;
    fetchChapters(book, translation);
});