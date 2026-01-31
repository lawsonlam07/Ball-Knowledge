const videoInput = document.getElementById('videoInput');
const videoPlayer = document.getElementById('videoPlayer');

videoInput.addEventListener('change', function() {
    const file = this.files[0];

    if (file) {
        // Create a temporary URL for the selected file
        const fileURL = URL.createObjectURL(file);
        
        // Set the video source to this URL
        videoPlayer.src = fileURL;
        
        // Optional: Auto-play when loaded
        videoPlayer.play();
    }
});