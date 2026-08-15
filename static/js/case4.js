let hotspotChart = null;
let iucrChart = null;
let communityChart = null;
let districtChart = null;
let hourlyChart = null;

document.addEventListener(
    "DOMContentLoaded",
    loadCase4
);


async function loadCase4() {

    try {

        const data =
            await fetchJSON(
                "/api/analyse?case=4"
            );

        console.log(
            "CASE 4 DATA:",
            data
        );

        // --------------------------------
        // KPIs
        // --------------------------------

        setText(
            "highestCommunity",
            data.kpis.highest_community
        );

        setText(
            "topIUCR",
            data.kpis.top_iucr
        );

        setText(
            "communityCount",
            formatNumber(
                data.kpis.community_count
            )
        );

        const outlierCount =
            document.getElementById(
                "outlierCount"
            );

        if (outlierCount) {
            outlierCount.textContent =
                formatNumber(
                    data.outliers.labels.length
                );
        }

        // --------------------------------
        // Hourly intensity
        // --------------------------------

        const hourlyCtx =
            document.getElementById(
                "hourlyChart"
            );

        if (hourlyCtx) {

            if (hourlyChart) {
                hourlyChart.destroy();
            }

            hourlyChart = new Chart(
                hourlyCtx,
                {
                    type: "line",

                    data: {
                        labels: data.crime_by_hour.labels,

                        datasets: [{
                            label: "Crimes per hour",
                            data: data.crime_by_hour.values,
                            borderColor: "#ff8a65",
                            backgroundColor: "rgba(255, 138, 101, 0.15)",
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
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
                            x: {
                                title: {
                                    display: true,
                                    text: "Hour of Day"
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: "Crime Count"
                                }
                            }
                        }
                    }
                }
            );
        }

        // --------------------------------
        // Hotspots
        // --------------------------------

        const hotspotCtx =
            document.getElementById(
                "hotspotChart"
            );

        if (hotspotCtx) {

            if (hotspotChart) {
                hotspotChart.destroy();
            }

            hotspotChart =
                new Chart(
                    hotspotCtx,
                    {
                        type: "bar",

                        data: {
                            labels:
                                data.hotspots.labels,

                            datasets: [{
                                label:
                                    "Crime Count",

                                data:
                                    data.hotspots.values,

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

        // --------------------------------
        // IUCR
        // --------------------------------

        const iucrCtx =
            document.getElementById(
                "iucrChart"
            );

        if (iucrCtx) {

            if (iucrChart) {
                iucrChart.destroy();
            }

            iucrChart =
                new Chart(
                    iucrCtx,
                    {
                        type: "bar",

                        data: {
                            labels:
                                data.iucr.labels,

                            datasets: [{
                                label:
                                    "Occurrences",

                                data:
                                    data.iucr.values,

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

        // --------------------------------
        // Community
        // --------------------------------

        const communityCtx =
            document.getElementById(
                "communityChart"
            );

        if (communityCtx) {

            if (communityChart) {
                communityChart.destroy();
            }

            communityChart =
                new Chart(
                    communityCtx,
                    {
                        type: "bar",

                        data: {
                            labels:
                                data.community.labels,

                            datasets: [{
                                label:
                                    "Crime Count",

                                data:
                                    data.community.values,

                                borderRadius:
                                    7
                            }]
                        },

                        options: {
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

        // --------------------------------
        // District
        // --------------------------------

        const districtCtx =
            document.getElementById(
                "districtChart"
            );

        if (districtCtx) {

            if (districtChart) {
                districtChart.destroy();
            }

            districtChart =
                new Chart(
                    districtCtx,
                    {
                        type: "doughnut",

                        data: {
                            labels:
                                data.district.labels,

                            datasets: [{
                                data:
                                    data.district.values
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
        // Heatmap
        // --------------------------------

        createCommunityHeatmap(
            data.heatmap
        );

        // --------------------------------
        // Correlation matrix
        // --------------------------------

        createCorrelationMatrix(
            data.correlation
        );

        // --------------------------------
        // Outliers
        // --------------------------------

        createOutliers(
            data.outliers
        );

        const insights = document.getElementById("geographicInsights");
        if (insights) {
            const peak = data.peak_hour;
            const topType = data.sql_reports.top5_crime_types[0];
            insights.innerHTML = `<p><strong>SQL views:</strong> ${data.sql_reports.views.join(", ")} are available for Pandas reporting.</p>
                <p><strong>Top crime type:</strong> ${topType.crime_type} (${formatPercent(topType.percentage)} of all crimes).</p>
                <p><strong>Highest crime area:</strong> Community ${data.kpis.highest_community}.</p>
                <p><strong>Top IUCR code:</strong> ${data.kpis.top_iucr}.</p>
                <p><strong>Peak time:</strong> ${peak.hour}:00 with ${formatNumber(peak.count)} crimes.</p>
                <p><strong>Priority communities:</strong> ${data.outliers.labels.length ? data.outliers.labels.join(", ") : "No IQR outliers detected"}.</p>`;
        }

    } catch (error) {

        showError(
            "Case 4 failed: " +
            error.message
        );
    }
}


function createCommunityHeatmap(
    data
) {

    const container =
        document.getElementById(
            "communityHeatmap"
        );

    if (!container) {
        return;
    }

    if (!data.labels.length) {

        container.innerHTML =
            "<p>No community data available.</p>";

        return;
    }

    const max =
        Math.max(
            ...data.values
        );

    let html =
        `<div class="community-heatmap-grid">`;

    data.labels.forEach(
        (label, index) => {

            const value =
                data.values[index];

            const intensity =
                max
                    ? value / max
                    : 0;

            html += `
                <div
                    class="community-heat-cell"
                    title="
                        Community ${label}
                        — ${formatNumber(value)} crimes
                    "
                    style="
                        opacity:
                        ${0.25 + intensity * 0.75};
                    "
                >

                    <span>
                        ${label}
                    </span>

                    <strong>
                        ${formatNumber(value)}
                    </strong>

                </div>
            `;
        }
    );

    html +=
        "</div>";

    container.innerHTML =
        html;
}


function createCorrelationMatrix(data) {

    const container =
        document.getElementById(
            "correlationMatrix"
        );

    if (!container) {
        return;
    }

    if (!data || !data.columns || !data.columns.length) {
        container.innerHTML =
            "<p>No correlation data available.</p>";
        return;
    }

    const rows = data.values;
    const headers = data.columns;

    let html = `
        <div class="correlation-grid">
            <div class="correlation-header-cell"></div>
    `;

    headers.forEach((header) => {
        html += `<div class="correlation-header-cell">${header}</div>`;
    });

    rows.forEach((row, rowIndex) => {
        html += `<div class="correlation-row-label">${headers[rowIndex]}</div>`;

        row.forEach((value) => {
            const strength = Math.abs(value);
            const hue = value >= 0 ? 220 - (strength * 180) : 10 + (strength * 180);
            const saturation = 70;
            const lightness = 90 - (strength * 45);

            html += `
                <div
                    class="correlation-cell"
                    style="background: hsl(${hue}, ${saturation}%, ${lightness}%); color: ${value >= 0 ? '#0b1220' : '#1a120b'};"
                    title="${headers[rowIndex]} vs ${headers[(rowIndex)]}: ${value.toFixed(3)}"
                >
                    ${Number(value).toFixed(2)}
                </div>
            `;
        });
    });

    html += `</div>`;
    container.innerHTML = html;
}


function createOutliers(data) {

    const container =
        document.getElementById(
            "outliers"
        );

    if (!container) {
        return;
    }

    if (!data.labels.length) {

        container.innerHTML = `
            <div class="empty-state">
                No statistical outliers detected.
            </div>
        `;

        return;
    }

    container.innerHTML = `
        <div class="outlier-summary">

            <div>
                <span>Q1</span>
                <strong>
                    ${formatNumber(data.q1)}
                </strong>
            </div>

            <div>
                <span>Q3</span>
                <strong>
                    ${formatNumber(data.q3)}
                </strong>
            </div>

            <div>
                <span>IQR</span>
                <strong>
                    ${formatNumber(data.iqr)}
                </strong>
            </div>

            <div>
                <span>Upper Bound</span>
                <strong>
                    ${formatNumber(
                        data.upper_bound
                    )}
                </strong>
            </div>

        </div>

        <div class="outlier-list">

            ${data.labels.map(
                (label, index) => `
                    <div class="outlier-item">

                        <span>
                            Community ${label}
                        </span>

                        <strong>
                            ${formatNumber(
                                data.values[index]
                            )}
                        </strong>

                    </div>
                `
            ).join("")}

        </div>
    `;
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
