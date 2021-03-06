(function() {
    registerPrintButtonHandler();
    return;

    function registerPrintButtonHandler() {
        var button = document.getElementById("las-print");

        if (!button || button.onclick === onPrintButtonClick) {
            setTimeout(registerPrintButtonHandler, 200);
            return;
        }

        button.onclick = onPrintButtonClick;
    }

    function onPrintButtonClick() {
        window.print();
    }
})();