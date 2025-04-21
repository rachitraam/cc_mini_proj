const { redirect } = require("react-router-dom");

async function shortenUrl() {
    const longUrl = document.getElementById('longUrl').value;
    const resultDiv = document.getElementById('shortenResult');

    if (!longUrl) {
        showError(resultDiv, 'Please enter a URL');
        return;
    }

    try {
        const response = await fetch('/api/shorten', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: longUrl })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(resultDiv, `
                Short URL: <a href="${data.short_url}" target="_blank">${data.short_url}</a>
                <br>
                <small>Original URL: ${data.long_url}</small>
            `);
        } else {
            showError(resultDiv, data.error || 'Failed to shorten URL');
        }
    } catch (error) {
        showError(resultDiv, 'Error connecting to the server');
    }
}

async function retrieveUrl() {
    const shortUrl = document.getElementById('shortUrl').value;
    const resultDiv = document.getElementById('retrieveResult');

    if (!shortUrl) {
        showError(resultDiv, 'Please enter a short URL or ID');
        return;
    }

    // Extract the ID from the short URL if full URL is provided
    const shortId = shortUrl.includes('/') ? shortUrl.split('/').pop() : shortUrl;
    console.log(shortId);
    console.log("Hi");
    try {
        console.log(shortId);
        const response = await fetch(`/api/retrieve/${shortId}`);
        console.log(response);
        if (response.ok) {
            const data = await response.json();
            showSuccess(resultDiv, `
                Original URL: <a href="${data.long_url}" target="_blank">${data.long_url}</a>
            `);
        } else {
            const data = await response.json();
            showError(resultDiv, data.error || 'URL not found');
        }
    } catch (error) {
        showError(resultDiv, 'Error connecting to the server', error);
    }
}

function showSuccess(element, message) {
    element.className = 'result success';
    element.innerHTML = message;
}

function showError(element, message) {
    element.className = 'result error';
    element.textContent = message;
} 