const audioPlayer = document.getElementById('player');
const playerCover = document.getElementById('playerCover');
const playerTitle = document.getElementById('playerTitle');
const addToPlaylistBtn = document.getElementById('addToPlaylistBtn');

let currentTrackElement = null;
let currentTrackId = null;
let currentTrackTitle = null;

function playAudio(audioUrl, coverUrl, title, artist, trackElement, trackId) {
    if (currentTrackElement) {
        currentTrackElement.classList.remove('active');
    }
    currentTrackElement = trackElement;
    currentTrackElement.classList.add('active')
    currentTrackId = trackId;
    currentTrackTitle = `${title} - ${artist}`;
    audioPlayer.src = audioUrl;
    audioPlayer.play();
    playerCover.src = coverUrl;
    playerTitle.textContent = `${title} - ${artist}`;
    audioPlayer.style.display = 'block';
    addToPlaylistBtn.style.display = 'block';
}

function openModalForCurrentTrack(){
    if (!currentTrackId) {
        alert('Сначала выберите трек!')
        return;
    }
    openModal(currentTrackId, currentTrackTitle);
}