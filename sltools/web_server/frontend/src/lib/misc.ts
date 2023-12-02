import Notiflix from "notiflix";
export const notify = Notiflix.Notify;

export function copyTextToClipboard(textToCopy: string) {
    const textArea = document.createElement("textarea");
    textArea.value = textToCopy;
    document.body.appendChild(textArea);

    textArea.select();
    document.execCommand("copy");

    document.body.removeChild(textArea);

    // Show a tooltip or feedback to indicate successful copying (optional)
    notify.info("Path copied to clipboard. (Ctrl+V to paste). Text:" + textToCopy);
}

export function getFileName(filePath: string) {
    const parts = filePath.split("/");
    return parts[parts.length - 1];
}
