/**
 * app.js --- необходимый клиентский функционал PromptFlow.
 *
 * - Единое подтверждение удаления для форм с атрибутом data-confirm
 *   (заменяет разрозненные inline confirm() в шаблонах).
 * - Автоскрытие flash-сообщений через 5 секунд.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Подтверждение удаления: одна точка входа для всех действий удаления.
    var forms = document.querySelectorAll("form[data-confirm]");
    forms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            var message = form.getAttribute("data-confirm") || "Подтвердите действие.";
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Автоскрытие flash-алертов Bootstrap через 5 секунд.
    var alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = null;
            if (typeof bootstrap !== "undefined" && bootstrap.Alert) {
                try {
                    bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                } catch (e) {
                    bsAlert = null;
                }
            }
            if (bsAlert) {
                bsAlert.close();
            } else {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(function () {
                    alert.remove();
                }, 500);
            }
        }, 5000);
    });
});
