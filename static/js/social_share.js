function shareRecipe(platform, url) {
    if (platform === 'email') {
        window.location.href = url;
        return;
    }

    const width = 600;
    const height = 400;
    const left = (window.innerWidth - width) / 2;
    const top = (window.innerHeight - height) / 2;

    window.open(
        url,
        '',
        `toolbar=no, location=no, directories=no, status=no, menubar=no, 
         scrollbars=no, resizable=no, copyhistory=no, width=${width}, 
         height=${height}, top=${top}, left=${left}`
    );
}

function copyLink() {
    const recipeUrl = document.getElementById('recipe-url').value;
    navigator.clipboard.writeText(recipeUrl).then(() => {
        const copyButton = document.getElementById('copy-link');
        copyButton.textContent = 'Copied!';
        setTimeout(() => {
            copyButton.textContent = 'Copy Link';
        }, 2000);
    });
}