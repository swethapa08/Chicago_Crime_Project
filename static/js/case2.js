let arrestChart = null;
let arrestYearChart = null;
let arrestCrimeChart = null;
let crimeDistributionChart = null;

document.addEventListener(
    "DOMContentLoaded",
    loadCase2
);


async function loadCase2() {

    try {

        const data =
            await fetchJSON(
                "/api/analyse?case=2"
            );

        console.log(
            "CASE 2 DATA:",
            data
        );

        setText(
            "totalArrests",
            formatNumber(
                data.kpis.total_arrests
            )
        );

        const arrestRateEl =
            document.getElementById(
                "arrestRate"
            ) || document.getElementById(
                "case2Rate"
            );

        if (arrestRateEl) {
            arrestRateEl.textContent =
                formatPercent(
                    data.kpis.arrest_rate
                );
        }

        setText(
            "highestArrestYear",
            data.kpis.highest_arrest_year
        );

        const highestRateEl =
            document.getElementById(
                "highestArrestRate"
            );

        if (highestRateEl) {
            highestRateEl.textContent =
                data.kpis.highest_arrest_rate
                    ? `Peak rate: ${formatPercent(data.kpis.highest_arrest_rate)}`
                    : "No arrest data";
        }

        // --------------------------------
        // Arrest Doughnut
        // --------------------------------

        const ctx =
            document.getElementById(
                "arrestOutcomeChart"
            );

        if (ctx) {

            if (arrestChart) {
                arrestChart.destroy();
            }

            arrestChart =
                new Chart(
                    ctx,
                    {
                        type: "doughnut",

                        data: {
                            labels:
                                data.outcome.labels,

                            datasets: [{
                                data:
                                    data.outcome.values
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

        // --------------------------------
        // Yearly arrest rate
        // --------------------------------

        const yearCtx =
            document.getElementById(
                "arrestYearChart"
            );

        if (yearCtx) {

            if (arrestYearChart) {
                arrestYearChart.destroy();
            }

            arrestYearChart =
                new Chart(
                    yearCtx,
                    {
                        type: "line",

                        data: {
                            labels:
                                data.yearly.labels,

                            datasets: [{
                                label:
                                    "Arrest Rate (%)",

                                data:
                                    data.yearly.values,

                                tension:
                                    0.35,

                                fill:
                                    true
                            }]
                        },

                        options: {
                            responsive: true,

                            maintainAspectRatio:
                                false,

                            scales: {
                                y: {
                                    beginAtZero:
                                        true,

                                    ticks: {
                                        callback:
                                            value =>
                                            value + "%"
                                    }
                                }
                            }
                        }
                    }
                );
        }

        // --------------------------------
        // Crime distribution doughnut
        // --------------------------------

        const distributionCtx =
            document.getElementById(
                "crimeDistributionChart"
            );

        if (distributionCtx) {

            if (crimeDistributionChart) {
                crimeDistributionChart.destroy();
            }

            const topCrimeLabels =
                data.arrests_by_crime.labels.slice(0, 6);
            const topCrimeValues =
                data.arrests_by_crime.values.slice(0, 6);

            crimeDistributionChart =
                new Chart(
                    distributionCtx,
                    {
                        type: "doughnut",

                        data: {
                            labels:
                                topCrimeLabels,

                            datasets: [{
                                data:
                                    topCrimeValues
                            }]
                        },

                        options: {
                            responsive:
                                true,

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

        // --------------------------------
        // Arrests by crime
        // --------------------------------

        const crimeCtx =
            document.getElementById(
                "arrestCrimeChart"
            );

        if (crimeCtx) {

            if (arrestCrimeChart) {
                arrestCrimeChart.destroy();
            }

            arrestCrimeChart =
                new Chart(
                    crimeCtx,
                    {
                        type: "bar",

                        data: {
                            labels:
                                data.arrests_by_crime.labels,

                            datasets: [{
                                label:
                                    "Arrests",

                                data:
                                    data.arrests_by_crime.values,

                                borderRadius:
                                    7
                            }]
                        },

                        options: {
                            indexAxis:
                                "y",

                            responsive:
                                true,

                            maintainAspectRatio:
                                false,

                            plugins: {
                                legend: {
                                    display:
                                        false
                                }
                            }
                        }
                    }
                );
        }

        const insights = document.getElementById("case2Insights");
        if (insights) {
            insights.innerHTML = `
                <p><strong>Most frequent crime:</strong> ${data.kpis.most_frequent_crime}</p>
                <p><strong>Arrest rate:</strong> ${formatPercent(data.kpis.arrest_rate)}</p>
                <p><strong>Highest crime month:</strong> Month ${data.kpis.highest_crime_month} (${formatNumber(data.kpis.highest_crime_month_count)} crimes)</p>
                <p><strong>Yearly comparison:</strong> peak arrest rate was ${formatPercent(data.kpis.highest_arrest_rate)} in ${data.kpis.highest_arrest_year}.</p>`;
        }

    } catch (error) {

        showError(
            "Case 2 failed: " +
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
