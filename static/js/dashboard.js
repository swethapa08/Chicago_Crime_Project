let crimeTrendChart = null;
let crimeCategoryChart = null;
let arrestChart = null;
let communityChart = null;


document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});


async function loadDashboard() {

    try {

        const data = await fetchJSON(
            "/api/statistics"
        );

        const stats = data.kpis || data;

        updateKPIs(stats);

        createCrimeTrendChart(
            data.yearly || {
                labels: [],
                values: []
            }
        );

        createCrimeCategoryChart(
            data.categories || {
                labels: [],
                values: []
            }
        );

        createArrestChart(
            data.arrests_chart || {
                labels: [],
                values: []
            }
        );

        createCommunityChart(
            data.communities || {
                labels: [],
                values: []
            }
        );

    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        showError(
            "Dashboard failed: " +
            error.message
        );
    }
}


function updateKPIs(data) {

    const totalCrimes = document.getElementById(
        "totalCrimes"
    );
    if (totalCrimes) {
        totalCrimes.textContent =
            formatNumber(data.total_crimes);
    }

    const arrests = document.getElementById(
        "arrests"
    );
    if (arrests) {
        arrests.textContent =
            formatNumber(data.arrests);
    }

    const domesticCases = document.getElementById(
        "domesticCases"
    );
    if (domesticCases) {
        domesticCases.textContent =
            formatNumber(data.domestic_cases);
    }

    const arrestRate = document.getElementById(
        "arrestRate"
    );
    if (arrestRate) {
        arrestRate.textContent =
            `${data.arrest_rate}%`;
    }
}


function formatNumber(value) {

    return Number(
        value || 0
    ).toLocaleString();
}


function createCrimeTrendChart(data) {

    const canvas =
        document.getElementById(
            "crimeTrendChart"
        );

    if (!canvas) return;

    if (crimeTrendChart) {
        crimeTrendChart.destroy();
    }

    const chartData =
        data || {
            labels: [],
            values: []
        };

    crimeTrendChart =
        new Chart(canvas, {

            type: "line",

            data: {

                labels:
                    chartData.labels || [],

                datasets: [{

                    label:
                        "Total Crimes",

                    data:
                        chartData.values || [],

                    tension: 0.35,

                    fill: true,
                    borderColor: "#60a5fa",
                    backgroundColor: "rgba(96, 165, 250, 0.18)"
                }]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
}


function createCrimeCategoryChart(data) {

    const canvas =
        document.getElementById(
            "crimeCategoryChart"
        );

    if (!canvas) return;

    if (crimeCategoryChart) {
        crimeCategoryChart.destroy();
    }

    const chartData =
        data || {
            labels: [],
            values: []
        };

    crimeCategoryChart =
        new Chart(canvas, {

            type: "bar",

            data: {

                labels:
                    chartData.labels || [],

                datasets: [{

                    label:
                        "Crime Count",

                    data:
                        chartData.values || [],

                    borderRadius: 8
                }]
            },

            options: {

                indexAxis: "y",

                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
}


function createArrestChart(data) {

    const canvas =
        document.getElementById(
            "arrestChart"
        );

    if (!canvas) return;

    if (arrestChart) {
        arrestChart.destroy();
    }

    const chartData =
        data || {
            labels: [],
            values: []
        };

    arrestChart =
        new Chart(canvas, {

            type: "doughnut",

            data: {

                labels:
                    chartData.labels || [],

                datasets: [{

                    data:
                        chartData.values || []
                }]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "70%"
            }
        });
}


function createCommunityChart(data) {

    const canvas =
        document.getElementById(
            "communityChart"
        );

    if (!canvas) return;

    if (communityChart) {
        communityChart.destroy();
    }

    const chartData =
        data || {
            labels: [],
            values: []
        };

    communityChart =
        new Chart(canvas, {

            type: "bar",

            data: {

                labels:
                    chartData.labels || [],

                datasets: [{

                    label:
                        "Crime Count",

                    data:
                        chartData.values || [],

                    borderRadius: 8
                }]
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
}


async function loadDataset() {

    try {

        const response = await fetch(
            "/api/ingest",
            {
                method: "POST"
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                "Dataset loading failed"
            );
        }

        alert(
            `Dataset loaded successfully.\n\n` +
            `Rows: ${data.rows_loaded.toLocaleString()}\n` +
            `Crime Types: ${data.unique_crime_types}\n` +
            `Communities: ${data.communities_loaded}`
        );

        await loadDashboard();

    } catch (error) {

        console.error(error);

        alert(
            "Data cannot be loaded: " +
            error.message
        );
    }
}