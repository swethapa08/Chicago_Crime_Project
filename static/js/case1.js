let case1Chart = null;
let case1DistributionChart = null;
let case1PercentageChart = null;

document.addEventListener(
    "DOMContentLoaded",
    loadCase1
);


async function loadCase1() {

    try {

        const data = await fetchJSON(
            "/api/analyse?case=1"
        );

        console.log(
            "CASE 1 DATA:",
            data
        );

        // -----------------------------
        // KPI
        // -----------------------------

        setText(
            "uniqueCrimeTypes",
            formatNumber(
                data.kpis.unique_crime_types
            )
        );

        setText(
            "mostCommonCrime",
            data.kpis.most_common_crime
        );

        setText(
            "topCrimeShare",
            formatPercent(
                data.kpis.top_crime_share
            )
        );

        // -----------------------------
        // Charts
        // -----------------------------

        const labels =
            data.top10.labels;

        const values =
            data.top10.values;

        const percentage =
            data.percentage.values;

        const barCanvas =
            document.getElementById(
                "crimeTypeChart"
            ) || document.getElementById(
                "case1BarChart"
            );

        if (barCanvas) {

            if (case1Chart) {
                case1Chart.destroy();
            }

            case1Chart =
                new Chart(
                    barCanvas,
                    {
                        type: "bar",

                        data: {
                            labels,

                            datasets: [{
                                label:
                                    "Crime Count",

                                data:
                                    values,

                                borderRadius:
                                    8
                            }]
                        },

                        options: {
                            responsive: true,

                            maintainAspectRatio:
                                false,

                            plugins: {
                                legend: {
                                    display:
                                        false
                                }
                            },

                            scales: {
                                x: {
                                    ticks: {
                                        autoSkip:
                                            false,

                                        maxRotation:
                                            45
                                    }
                                },

                                y: {
                                    beginAtZero:
                                        true
                                }
                            }
                        }
                    }
                );
        }

        const distributionCanvas =
            document.getElementById(
                "case1DoughnutChart"
            );

        if (distributionCanvas) {

            if (case1DistributionChart) {
                case1DistributionChart.destroy();
            }

            case1DistributionChart =
                new Chart(
                    distributionCanvas,
                    {
                        type: "doughnut",

                        data: {
                            labels:
                                labels.slice(0, 6),

                            datasets: [{
                                data:
                                    values.slice(0, 6)
                            }]
                        },

                        options: {
                            responsive: true,

                            maintainAspectRatio:
                                false,

                            plugins: {
                                legend: {
                                    position:
                                        "bottom"
                                }
                            }
                        }
                    }
                );
        }

        const percentCanvas =
            document.getElementById(
                "case1PercentageChart"
            ) || document.getElementById(
                "crimePercentageChart"
            );

        if (percentCanvas) {

            if (case1PercentageChart) {
                case1PercentageChart.destroy();
            }

            case1PercentageChart =
                new Chart(
                    percentCanvas,
                    {
                        type: "doughnut",

                        data: {
                            labels,

                            datasets: [{
                                data:
                                    percentage
                            }]
                        },

                        options: {
                            responsive: true,

                            maintainAspectRatio:
                                false,

                            plugins: {
                                legend: {
                                    position:
                                        "bottom"
                                }
                            }
                        }
                    }
                );
        }

        // -----------------------------
        // Table / insights
        // -----------------------------

        const table =
            document.getElementById(
                "crimeTableBody"
            );

        if (table) {

            table.innerHTML =
                data.table.map(
                    row => `
                    <tr>
                        <td>${row.crime}</td>
                        <td>${formatNumber(row.count)}</td>
                        <td>${row.percentage}%</td>
                    </tr>
                    `
                ).join("");
        }

        const insights =
            document.getElementById(
                "case1Insights"
            );

        if (insights && data.table?.length) {
            insights.innerHTML =
                data.table.slice(0, 3).map(
                    row => `
                        <div class="insight-item">
                            <strong>${row.crime}</strong>
                            <span>${row.percentage}% of all reported crime</span>
                        </div>
                    `
                ).join("");
        }

    } catch (error) {

        showError(
            "Case 1 failed: " +
            error.message
        );
    }
}


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent =
            value;
    }
}