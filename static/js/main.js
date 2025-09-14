document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.5s';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });

    const shareButtons = document.querySelectorAll('.share-button');
    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (navigator.share) {
                const title = this.dataset.title || 'Check out this zine!';
                const url = this.dataset.url || window.location.href;
                navigator.share({ title, url })
                    .catch(err => console.log('Error sharing:', err));
            } else {
                const url = this.dataset.url || window.location.href;
                navigator.clipboard.writeText(url)
                    .then(() => alert('Link copied to clipboard!'))
                    .catch(err => console.log('Error copying:', err));
            }
        });
    });
});