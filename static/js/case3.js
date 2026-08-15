let hourlyChart = null;
let monthlyChart = null;
let dailyChart = null;

document.addEventListener(
    "DOMContentLoaded",
    loadCase3
);


async function loadCase3() {

    try {

        const data =
            await fetchJSON(
                "/api/analyse?case=3"
            );

        console.log(
            "CASE 3 DATA:",
            data
        );

        // --------------------------------
        // Hourly
        // --------------------------------

        const hourlyCtx =
            document.getElementById(
                "hourlyChart"
            ) || document.getElementById(
                "hourChart"
            );

        if (hourlyCtx) {

            if (hourlyChart) {
                hourlyChart.destroy();
            }

            hourlyChart =
                new Chart(
                    hourlyCtx,
                    {
                        type: "line",

                        data: {
                            labels:
                                data.hourly.labels,

                            datasets: [{
                                label:
                                    "Crimes",

                                data:
                                    data.hourly.values,

                                tension:
                                    0.35,

                                fill:
                                    true
                            }]
                        },

                        options: {
                            responsive: true,

                            maintainAspectRatio:
                                false
                        }
                    }
                );
        }

        // --------------------------------
        // Monthly
        // --------------------------------

        const monthlyCtx =
            document.getElementById(
                "monthlyChart"
            );

        if (monthlyCtx) {

            if (monthlyChart) {
                monthlyChart.destroy();
            }

            monthlyChart =
                new Chart(
                    monthlyCtx,
                    {
                        type: "bar",

                        data: {
                            labels:
                                data.monthly.labels,

                            datasets: [{
                                label:
                                    "Crimes",

                                data:
                                    data.monthly.values,

                                borderRadius:
                                    7
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
                            }
                        }
                    }
                );
        }

        // --------------------------------
        // Day
        // --------------------------------

        const dailyCtx =
            document.getElementById(
                "dailyChart"
            );

        if (dailyCtx) {

            if (dailyChart) {
                dailyChart.destroy();
            }

            dailyChart =
                new Chart(
                    dailyCtx,
                    {
                        type: "bar",

                        data: {
                            labels:
                                data.daily.labels,

                            datasets: [{
                                label:
                                    "Crimes",

                                data:
                                    data.daily.values,

                                borderRadius:
                                    7
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
                            }
                        }
                    }
                );
        }

        // --------------------------------
        // Heatmap
        // --------------------------------

        createHeatmap(
            data.heatmap
        );

        // --------------------------------
        // Correlation
        // --------------------------------

        createCorrelation(
            data.correlation
        );

        // --------------------------------
        // Outliers
        // --------------------------------

        createOutliers(
            data.outliers
        );

        const insights = document.getElementById("case3Insights");
        if (insights) {
            const peak = data.hourly.values.indexOf(Math.max(...data.hourly.values));
            insights.innerHTML = `<p><strong>Peak crime hour:</strong> ${peak}:00 (${formatNumber(data.hourly.values[peak])} crimes).</p>
                <p><strong>Mean crimes per community:</strong> ${formatNumber(data.community_clusters.mean_crime_count)} across ${formatNumber(data.community_clusters.community_areas_analyzed)} areas.</p>
                <p><strong>Community outliers:</strong> ${data.outliers.labels.length ? data.outliers.labels.join(", ") : "None detected"}.</p>
                <p><strong>IQR upper bound:</strong> ${formatNumber(data.outliers.upper_bound)} crimes per community.</p>`;
        }

    } catch (error) {

        showError(
            "Case 3 failed: " +
            error.message
        );
    }
}


function createHeatmap(data) {

    const container =
        document.getElementById(
            "timeHeatmap"
        ) || document.querySelector(
            ".heatmap-wrapper"
        );

    if (!container) {
        return;
    }

    let max = 0;

    data.values.forEach(
        row => {

            row.forEach(
                value => {

                    if (value > max) {
                        max = value;
                    }

                }
            );

        }
    );

    let html =
        `<div class="heatmap-grid">`;

    html +=
        `<div class="heatmap-cell header"></div>`;

    data.x.forEach(
        day => {

            html += `
                <div class="heatmap-cell header">
                    ${day.substring(0, 3)}
                </div>
            `;

        }
    );

    data.y.forEach(
        (month, rowIndex) => {

            html += `
                <div class="heatmap-cell header">
                    ${month}
                </div>
            `;

            data.x.forEach(
                (day, colIndex) => {

                    const value =
                        data.values[
                            rowIndex
                        ][colIndex];

                    const intensity =
                        max
                            ? value / max
                            : 0;

                    const hue =
                        220 - intensity * 170;

                    const lightness =
                        25 + intensity * 35;

                    html += `
                        <div
                            class="heatmap-cell"
                            title="${month} / ${day}: ${value}"
                            style="
                                background:
                                hsla(${hue}, 82%, ${lightness}%, 0.9);
                                color:
                                ${intensity > 0.68 ? '#f8fafc' : '#e2e8f0'};
                                border-color:
                                rgba(148,163,184,0.12);
                            "
                        >
                            ${value}
                        </div>
                    `;
                }
            );

        }
    );

    html += "</div>";

    container.innerHTML =
        html;
}


function createCorrelation(data) {

    const container =
        document.getElementById(
            "correlationMatrix"
        );

    if (!container) {
        return;
    }

    let html =
        `<div class="correlation-grid" style="grid-template-columns: 110px repeat(${data.labels.length}, minmax(54px, 1fr));">`;

    html +=
        `<div class="correlation-header">&nbsp;</div>`;

    data.labels.forEach(
        label => {

            html += `
                <div class="correlation-header">
                    ${label}
                </div>
            `;

        }
    );

    data.values.forEach(
        (row, i) => {

            html += `
                <div class="correlation-label">
                    ${data.labels[i]}
                </div>
            `;

            row.forEach(
                value => {

                    html += `
                        <div
                            class="correlation-cell"
                            title="${value}"
                        >
                            ${Number(value).toFixed(2)}
                        </div>
                    `;

                }
            );

        }
    );

    html += "</div>";

    container.innerHTML =
        html;
}


function createOutliers(data) {

    const container =
        document.getElementById(
            "outlierList"
        ) || document.getElementById(
            "iqrStats"
        );

    if (!container) {
        return;
    }

    if (!data.labels.length) {

        container.innerHTML =
            "<p>No statistical outliers detected.</p>";

        return;
    }

    container.innerHTML = `
        <p>
            IQR lower bound:
            <strong>
                ${formatNumber(data.lower_bound ?? 0)}
            </strong>
        </p>
        <p>
            IQR upper bound:
            <strong>
                ${formatNumber(data.upper_bound)}
            </strong>
        </p>

        ${data.labels.map(
            (label, index) => `
                <div class="outlier-item">
                    <span>${label}</span>
                    <strong>
                        ${formatNumber(
                            data.values[index]
                        )}
                    </strong>
                </div>
            `
        ).join("")}
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
