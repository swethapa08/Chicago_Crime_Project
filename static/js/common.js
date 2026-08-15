async function fetchJSON(url, options = {}) {

    try {

        const response = await fetch(
            url,
            options
        );

        const text = await response.text();

        let data;

        try {
            data = JSON.parse(text);
        } catch (e) {

            throw new Error(
                "Server returned invalid JSON"
            );
        }

        if (!response.ok) {

            throw new Error(
                data.error ||
                `HTTP ${response.status}`
            );
        }

        if (
            data.status === "error"
        ) {

            throw new Error(
                data.error ||
                "API error"
            );
        }

        return data;

    } catch (error) {

        console.error(
            "API Error:",
            error
        );

        throw error;
    }
}


function showError(message) {

    console.error(message);

    const containers =
        document.querySelectorAll(
            ".api-error"
        );

    containers.forEach(
        container => {

            container.textContent =
                message;

            container.style.display =
                "block";
        }
    );
}


function formatNumber(value) {

    return Number(
        value || 0
    ).toLocaleString(
        "en-IN"
    );
}


function formatPercent(value) {

    return `${Number(
        value || 0
    ).toFixed(2)}%`;
}