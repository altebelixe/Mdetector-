chrome.tabs.onActivated.addListener(async (activeInfo) => {
    try {
        let tab = await chrome.tabs.get(activeInfo.tabId);
        sendUrlToServer(tab.url, tab.id);
    } catch (error) {
        console.error('Error getting tab:', error);
    }
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        sendUrlToServer(tab.url, tabId);
    }
});

async function sendUrlToServer(url, tabId) {
    try {
        let response = await fetch('https://mdetector-api.jusyst.easypanel.host/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "url": url })
        });

        console.log(response)

        if (response.ok) {
            let data = await response.json();
            console.log('Server response:', data);

            if (data.prediction === "malicious") {
                blockMaliciousSite(tabId);
            }
        } else {
            console.error('Server error:', response.statusText);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

function blockMaliciousSite(tabId) {
    chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: () => {
            document.body.innerHTML = '';
            document.body.style.backgroundColor = 'red';
            document.body.style.color = 'white';
            document.body.style.display = 'flex';
            document.body.style.justifyContent = 'center';
            document.body.style.alignItems = 'center';
            document.body.style.height = '100vh';
            document.body.style.margin = '0';
            document.body.style.fontSize = '24px';
            document.body.innerText = 'Site malveillant bloqué';
        }
    });
}
