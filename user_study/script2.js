// Get the video elements
const videos = document.querySelectorAll('.videoItem');

// Add click event listener to each video element
videos.forEach(video => {
  video.addEventListener('click', () => {
    // Pause all videos
    videos.forEach(v => {
      if (v !== video) {
        v.pause();
      }
    });
  });
});

