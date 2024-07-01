document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const progressBar = document.getElementById('progress');
    const playPauseButton = document.getElementById('play-pause');

    video.addEventListener('timeupdate', () => {
        const progress = (video.currentTime / video.duration) * 100;
        progressBar.value = progress;
    });

    progressBar.addEventListener('input', () => {
        const seekTime = (progressBar.value / 100) * video.duration;
        video.currentTime = seekTime;
    });

    progressBar.addEventListener('change', () => {
        if (video.paused) {
            video.pause();
        }
    });

    playPauseButton.addEventListener('click', () => {
        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    });

    video.addEventListener('play', () => {
        playPauseButton.classList.remove('play');
        playPauseButton.classList.add('pause');
    });

    video.addEventListener('pause', () => {
        playPauseButton.classList.remove('pause');
        playPauseButton.classList.add('play');
    });

    // Handle touch events for mobile
    progressBar.addEventListener('touchstart', (e) => {
        const touch = e.touches[0];
        const seekTime = ((touch.clientX - progressBar.getBoundingClientRect().left) / progressBar.offsetWidth) * video.duration;
        video.currentTime = seekTime;
    });

    progressBar.addEventListener('touchmove', (e) => {
        const touch = e.touches[0];
        const seekTime = ((touch.clientX - progressBar.getBoundingClientRect().left) / progressBar.offsetWidth) * video.duration;
        video.currentTime = seekTime;
    });
});