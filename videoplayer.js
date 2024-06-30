document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const progressBar = document.getElementById('progress');

    video.addEventListener('timeupdate', () => {
        const progress = (video.currentTime / video.duration) * 100;
        progressBar.value = progress;
    });

    progressBar.addEventListener('input', () => {
        const seekTime = (progressBar.value / 100) * video.duration;
        video.currentTime = seekTime;
    });

    progressBar.addEventListener('click', () => {
        if (video.paused) {
            video.play();
            progressBar.classList.remove('play');
            progressBar.classList.add('pause');
        } else {
            video.pause();
            progressBar.classList.remove('pause');
            progressBar.classList.add('play');
        }
    });

    video.addEventListener('play', () => {
        progressBar.classList.remove('play');
        progressBar.classList.add('pause');
    });

    video.addEventListener('pause', () => {
        progressBar.classList.remove('pause');
        progressBar.classList.add('play');
    });
});