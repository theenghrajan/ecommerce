if (!customElements.get('media-gallery')) {
	customElements.define('media-gallery', class MediaGallery extends HTMLElement {
		constructor() {
			super();
			this.elements = {
				mains: this.querySelectorAll('.product-media-main'),
				thumbnails: this.querySelectorAll('.product-media-thumbnail'),
			};

			if (!this.elements.thumbnails.length) {
				return;
			}

			this.elements.thumbnails.forEach((thumbnail) => {
				const mediaToggle = thumbnail.querySelector('button');
				if (!mediaToggle) {
					return;
				}
				mediaToggle.addEventListener('click', this.setActiveMedia.bind(this, mediaToggle.dataset.mediaId, false));
			});
		}

		setActiveMedia(mediaId, prepend) {
			const thumbnail = [...this.elements.thumbnails].find((element) => {
				return element.dataset.mediaId === mediaId.toString();
			});
			const isActive = thumbnail?.classList.contains('is-active');

			if (!thumbnail || isActive) {
				return;
			}

			const index = [...this.elements.thumbnails].indexOf(thumbnail);
			const activeMainMedia = [...this.elements.mains].find((element) => {
				return element.classList.contains('is-active');
			});
			this.elements.thumbnails.forEach((thumb) => {
				thumb.classList.remove('is-active');
			});
			activeMainMedia.classList.remove('is-active');

			const nextMainMedia = this.elements.mains[index];
			nextMainMedia.classList.add('is-active');
			thumbnail.classList.add('is-active');
			this.playActiveMedia(nextMainMedia);

			if (prepend) {
				thumbnail.parentElement.prepend(thumbnail);
			} else {
				thumbnail.scrollIntoView({
					behavior: 'smooth',
					block: 'nearest',
				});
			}
		}

		playActiveMedia(activeItem) {
			window.pauseAllMedia();
			const deferredMedia = activeItem.querySelector('deferred-media');

			if (deferredMedia) {
				deferredMedia.loadContent(false);
			}
		}
	});
}
