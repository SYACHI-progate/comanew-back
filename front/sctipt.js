document.addEventListener('DOMContentLoaded', () => {
    const viewer = document.querySelector('.manga-viewer');
    const slides = document.querySelectorAll('.manga-slide');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const newsLink = document.getElementById('news-link');
    let currentSlide = 0;

    function updateSlides(offset = 0) {
        slides.forEach((slide, index) => {
            slide.style.transform = `translateY(${100 * (index - currentSlide) + offset}%)`;
        });
        updateNewsLink();
    }

    function updateNewsLink() {
        const currentNewsUrl = slides[currentSlide].dataset.newsUrl;
        newsLink.href = currentNewsUrl;
    }

    function nextSlide() {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            updateSlides();
        }
    }

    function prevSlide() {
        if (currentSlide > 0) {
            currentSlide--;
            updateSlides();
        }
    }

    // タッチスワイプの処理
    let startY;
    let isDragging = false;

    viewer.addEventListener('touchstart', (e) => {
        startY = e.touches[0].clientY;
        isDragging = true;
    });

    viewer.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        const currentY = e.touches[0].clientY;
        const diff = startY - currentY;
        const translateY = -diff / viewer.clientHeight * 100;
        updateSlides(translateY);
    });

    viewer.addEventListener('touchend', (e) => {
        if (!isDragging) return;
        isDragging = false;
        const endY = e.changedTouches[0].clientY;
        const diff = startY - endY;
        if (Math.abs(diff) > 50) { // 50px以上のスワイプで切り替え
            if (diff > 0) {
                nextSlide();
            } else {
                prevSlide();
            }
        } else {
            updateSlides(); // 元の位置に戻す
        }
    });

    // フルスクリーン機能
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            } else if (document.documentElement.mozRequestFullScreen) { // Firefox
                document.documentElement.mozRequestFullScreen();
            } else if (document.documentElement.webkitRequestFullscreen) { // Chrome, Safari and Opera
                document.documentElement.webkitRequestFullscreen();
            } else if (document.documentElement.msRequestFullscreen) { // IE/Edge
                document.documentElement.msRequestFullscreen();
            }
            fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) { // Firefox
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { // IE/Edge
                document.msExitFullscreen();
            }
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        }
    }

    fullscreenBtn.addEventListener('click', toggleFullscreen);

    // ナビゲーションボタンのイベントリスナーを追加
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // 初期表示
    updateSlides();
});

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered: ', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed: ', error);
            });
    });
}
