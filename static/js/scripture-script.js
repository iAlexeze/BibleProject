// Javascript setup for scripture.html

// Speech synthesis state management
let isPlayingAll = false;
let currentVerseIndex = 0;
let utterances = [];
let lastPlayedVerseIndex = -1;

// Function for the speakVerse function
function speakVerse(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1;
        utterance.pitch = 1;

        // Add event listeners for verse completion
        utterance.onend = function() {
            if (isPlayingAll) {
                currentVerseIndex++;
                if (currentVerseIndex < utterances.length) {
                    window.speechSynthesis.speak(utterances[currentVerseIndex]);
                } else {
                    stopPlayingAll();
                }
            }
            // Track the last played verse
            lastPlayedVerseIndex = currentVerseIndex;
        };

        utterances.push(utterance);
        window.speechSynthesis.speak(utterance);
    } else {
        alert("Your browser does not support text-to-speech.");
    }
}

// Function to play all verses
function playAll() {
    if (!isPlayingAll) {
        isPlayingAll = true;
        utterances = [];

        // Get all verses from the page
        const verses = document.querySelectorAll('.verse-text');

        // Start from where we left off, or from the beginning if this is the first time
        const startIndex = lastPlayedVerseIndex === -1 ? 0 : lastPlayedVerseIndex;

        // Play all verses starting from the last played index
        for (let i = startIndex; i < verses.length; i++) {
            speakVerse(verses[i].textContent);
        }

        // Update button appearance
        document.getElementById('playIcon').textContent = '⏸';
        document.getElementById('playText').textContent = 'Pause';
    } else {
        stopPlayingAll();
    }
}

// Function to stop playing all verses
function stopPlayingAll() {
    isPlayingAll = false;
    window.speechSynthesis.cancel();
    utterances = [];
 //   currentVerseIndex = 0;

    // Reset button appearance
    document.getElementById('playIcon').textContent = '▶';
    document.getElementById('playText').textContent = 'Play';
}

// Initialize play all button
document.getElementById('playAllButton').addEventListener('click', playAll);

// Add this initialization code right after your existing script functions
window.onload = function() {
    // Call fetchTranslations immediately when the page loads
    fetchTranslations();
};

// Modify your existing fetchTranslations function to include error handling
async function fetchTranslations() {
    try {
        const response = await fetch('/translations');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const translations = await response.json();
        const translationSelect = document.getElementById('translation');

        // Clear existing options except the placeholder
        translationSelect.innerHTML = '<option value="" disabled selected>Switch Translation</option>';

        translations.forEach((translation) => {
            const option = document.createElement('option');
            option.value = translation.identifier;
            option.textContent = translation.name;
            translationSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching translations:', error);
        // Show error to user
        const translationSelect = document.getElementById('translation');
        translationSelect.innerHTML = '<option value="" disabled>Error loading translations</option>';
    }
}

// Replace the existing translationSelect event listener with this updated version
document.addEventListener('DOMContentLoaded', () => {
    stopPlayingAll();
    const translationSelect = document.getElementById('translation');

    function getCurrentUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            book: urlParams.get('book'),
            chapter: urlParams.get('chapter')
        };
    }

    translationSelect.addEventListener('change', async (event) => {
        const { book, chapter } = getCurrentUrlParams();

        // Create new URL with updated translation
        const baseUrl = '/read';
        const params = new URLSearchParams({
            translation: event.target.value,
            book,
            chapter
        });

        // Navigate to the new URL
        window.location.href = `${baseUrl}?${params.toString()}`;
    });
});

// Function to update the chapter in the URI
function updateChapter(delta) {
// Get the current URL
const url = new URL(window.location.href);

// Extract the current chapter from the URL
const currentChapter = parseInt(url.searchParams.get('chapter'));

// Calculate the new chapter
const newChapter = currentChapter + delta;

// Update the chapter in the URL
url.searchParams.set('chapter', newChapter);

// Redirect to the new URL
window.location.href = url.toString();
}

// Add event listeners to the buttons
document.getElementById('prevChapter').addEventListener('click', function (e) {
e.preventDefault(); // Prevent the default link behavior
updateChapter(-1); // Decrease the chapter by 1
});

document.getElementById('nextChapter').addEventListener('click', function (e) {
e.preventDefault(); // Prevent the default link behavior
updateChapter(1); // Increase the chapter by 1
});