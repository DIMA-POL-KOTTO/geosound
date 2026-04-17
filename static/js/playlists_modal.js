const modal = document.getElementById('playlistsModal');
const trackIdInput = document.getElementById('modalTrackId');
const trackTitleInput = document.getElementById('modalTrackTitle');

function closeModal() {
    modal.style.display = 'none';
}

function openModal(trackId, trackTitle) {
    trackIdInput.value = trackId;
    trackTitleInput.textContent = trackTitle;
    modal.style.display = 'block';
}

window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}