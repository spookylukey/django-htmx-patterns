(function () {
    document.body.addEventListener("htmx:afterSettle", function(detail) {
        const dialog = detail.target.querySelector('dialog[data-onload-showmodal]');
        if (dialog) {
            dialog.addEventListener("close", () => {
                // Cleanup and avoid interaction issues by removing entirely
                dialog.remove();
            });
            dialog.showModal();
        };
    });

    document.body.addEventListener('closeModal', function() {
        document.querySelector('dialog[open]').close();
    });

})();
