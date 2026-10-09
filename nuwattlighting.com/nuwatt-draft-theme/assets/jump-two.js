const track = document.querySelector('.carousel-track');
const slides = Array.from(track.children);
const leftButton = document.getElementById('left-button');
const rightButton = document.getElementById('right-button');
const slideWidth = slides[0].getBoundingClientRect().width;

let startPos = 0;
let endPos = 0;

const setSlidePosition = (slide, index) => {
    slide.style.left = slideWidth * index + 'px';
};
slides.forEach(setSlidePosition);

const moveToSlide = (track, currentSlide, targetSlide) => {
    track.style.transform = 'translateX(-' + targetSlide.style.left + ')';
    currentSlide.classList.remove('current-slide');
    targetSlide.classList.add('current-slide');
};

// Move slides to the right
rightButton.addEventListener('click', () => {
    const currentSlide = track.querySelector('.current-slide');
    const nextSlide = currentSlide.nextElementSibling;

    if (nextSlide) {
        moveToSlide(track, currentSlide, nextSlide);
    }
});

// Move slides to the left
leftButton.addEventListener('click', () => {
    const currentSlide = track.querySelector('.current-slide');
    const prevSlide = currentSlide.previousElementSibling;

    if (prevSlide) {
        moveToSlide(track, currentSlide, prevSlide);
    }
});

// Touch event handlers
const handleTouchStart = (e) => {
    startPos = e.touches[0].clientX;
};

const handleTouchMove = (e) => {
    endPos = e.touches[0].clientX;
};

const handleTouchEnd = () => {
    const currentSlide = track.querySelector('.current-slide');
    if (startPos - endPos > 50) {
        // Swipe left (move to the next slide)
        const nextSlide = currentSlide.nextElementSibling;
        if (nextSlide) {
            moveToSlide(track, currentSlide, nextSlide);
        }
    } else if (endPos - startPos > 50) {
        // Swipe right (move to the previous slide)
        const prevSlide = currentSlide.previousElementSibling;
        if (prevSlide) {
            moveToSlide(track, currentSlide, prevSlide);
        }
    }
};

track.addEventListener('touchstart', handleTouchStart);
track.addEventListener('touchmove', handleTouchMove);
track.addEventListener('touchend', handleTouchEnd);
