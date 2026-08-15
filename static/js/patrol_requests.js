const apiUrl = "/api/patrol-requests";
const form = document.getElementById("patrolRequestForm");
const body = document.getElementById("patrolRequestsBody");
const errorBox = document.getElementById("formError");

function value(id) {
    return document.getElementById(id).value.trim();
}

function optionalNumber(id, parser) {
    const input = value(id);
    return input === "" ? null : parser(input);
}

function payload() {
    return {
        ward_no: optionalNumber("wardNo", Number),
        district_code: optionalNumber("districtCode", Number),
        community_code: value("communityCode") || null,
        patrol_area: value("patrolArea"),
        priority: value("priority"),
        reason: value("reason") || null,
        requested_by: value("requestedBy") || null,
        assigned_officers: optionalNumber("assignedOfficers", Number) ?? 0,
        status: value("status"),
        perimeter_radius: optionalNumber("perimeterRadius", Number)
    };
}

function escapeHtml(text) {
    return String(text ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#039;", '"': "&quot;" })[char]);
}

function resetForm() {
    form.reset();
    document.getElementById("requestId").value = "";
    document.getElementById("assignedOfficers").value = 0;
    document.getElementById("status").value = "PENDING";
    document.getElementById("priority").value = "HIGH";
    document.getElementById("formTitle").textContent = "Create Patrol Request";
    document.getElementById("submitButton").textContent = "Create Request";
    document.getElementById("cancelEdit").hidden = true;
    errorBox.style.display = "none";
}

async function loadRequests() {
    body.innerHTML = '<tr><td colspan="8" class="loading">Loading patrol requests…</td></tr>';
    try {
        const response = await fetch(apiUrl);
        const requests = await response.json();
        if (!response.ok) throw new Error(requests.error || "Unable to load patrol requests.");
        document.getElementById("requestCount").textContent = `${requests.length} request${requests.length === 1 ? "" : "s"} recorded`;
        if (!requests.length) {
            body.innerHTML = '<tr><td colspan="8" class="empty-table">No patrol requests have been created yet.</td></tr>';
            return;
        }
        body.innerHTML = requests.map(item => `
            <tr>
                <td>#${item.request_id}</td><td><strong>${escapeHtml(item.patrol_area)}</strong><small>${escapeHtml(item.reason || "No reason provided")}</small></td>
                <td>${item.district_code ?? "—"}</td><td><span class="priority priority-${String(item.priority).toLowerCase()}">${escapeHtml(item.priority)}</span></td>
                <td>${item.assigned_officers}</td><td>${item.perimeter_radius == null ? "—" : `${item.perimeter_radius} km`}</td>
                <td><span class="status status-${String(item.status).toLowerCase()}">${escapeHtml(item.status)}</span></td>
                <td class="row-actions"><button class="table-btn" onclick="editRequest(${item.request_id})">Edit</button><button class="table-btn danger" onclick="deleteRequest(${item.request_id})">Delete</button></td>
            </tr>`).join("");
    } catch (error) {
        body.innerHTML = `<tr><td colspan="8" class="empty-table">${escapeHtml(error.message)}</td></tr>`;
    }
}

async function editRequest(id) {
    const response = await fetch(`${apiUrl}/${id}`);
    const item = await response.json();
    if (!response.ok) return;
    document.getElementById("requestId").value = item.request_id;
    const mappings = { wardNo: "ward_no", districtCode: "district_code", communityCode: "community_code", patrolArea: "patrol_area", priority: "priority", reason: "reason", requestedBy: "requested_by", assignedOfficers: "assigned_officers", status: "status", perimeterRadius: "perimeter_radius" };
    Object.entries(mappings).forEach(([id, key]) => document.getElementById(id).value = item[key] ?? "");
    document.getElementById("formTitle").textContent = `Edit Patrol Request #${item.request_id}`;
    document.getElementById("submitButton").textContent = "Save Changes";
    document.getElementById("cancelEdit").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
}

async function deleteRequest(id) {
    if (!window.confirm(`Delete patrol request #${id}?`)) return;
    const response = await fetch(`${apiUrl}/${id}`, { method: "DELETE" });
    if (response.ok) loadRequests();
}

form.addEventListener("submit", async event => {
    event.preventDefault();
    const id = value("requestId");
    const response = await fetch(id ? `${apiUrl}/${id}` : apiUrl, { method: id ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload()) });
    const result = await response.json();
    if (!response.ok) {
        errorBox.textContent = result.error || "Unable to save the patrol request.";
        errorBox.style.display = "block";
        return;
    }
    resetForm();
    loadRequests();
});

document.getElementById("cancelEdit").addEventListener("click", resetForm);
document.getElementById("refreshRequests").addEventListener("click", loadRequests);
loadRequests();
