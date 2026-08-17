import json
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from .ingestion import ingest_data
from .analysis import (
    get_statistics,
    case1_crime_type_analysis,
    case2_arrest_analysis,
    case3_time_analysis,
    case4_geographic_analysis
)
from .database import (
    get_connection,
    ensure_patrol_requests_table,
    sync_patrol_requests_to_csv 
)


api = Blueprint(
    "api",
    __name__
)


PATROL_REQUEST_FIELDS = {
    "ward_no", "district_code", "community_code", "patrol_area", "priority",
    "reason", "requested_by", "assigned_officers", "status", "perimeter_radius"
}


def patrol_request_to_dict(row):
    return dict(row)


def validate_patrol_payload(data, partial=False):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    unknown_fields = set(data) - PATROL_REQUEST_FIELDS
    if unknown_fields:
        return None, f"Unsupported field(s): {', '.join(sorted(unknown_fields))}."

    required_fields = {"ward_no", "district_code", "community_code", "patrol_area", "priority"}
    if not partial:
        missing_fields = [field for field in required_fields if not str(data.get(field, "")).strip()]
        if missing_fields:
            return None, f"Missing required field(s): {', '.join(missing_fields)}."

    cleaned = {field: value for field, value in data.items() if field in PATROL_REQUEST_FIELDS}
    for field in ("patrol_area", "priority", "reason", "requested_by", "status", "community_code"):
        if field in cleaned and cleaned[field] is not None:
            cleaned[field] = str(cleaned[field]).strip()

    for field in ("patrol_area", "priority"):
        if field in cleaned and not cleaned[field]:
            return None, f"{field} cannot be empty."

    for field in ("ward_no", "district_code", "assigned_officers"):
        if field in cleaned and cleaned[field] is not None:
            try:
                cleaned[field] = int(cleaned[field])
            except (TypeError, ValueError):
                return None, f"{field} must be an integer."

    if cleaned.get("assigned_officers") is not None and cleaned.get("assigned_officers", 0) < 0:
        return None, "assigned_officers cannot be negative."

    if "perimeter_radius" in cleaned and cleaned["perimeter_radius"] is not None:
        try:
            cleaned["perimeter_radius"] = float(cleaned["perimeter_radius"])
        except (TypeError, ValueError):
            return None, "perimeter_radius must be a number."
        if cleaned["perimeter_radius"] < 0:
            return None, "perimeter_radius cannot be negative."

    return cleaned, None


def patrol_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def print_api_result(api_name, result):
    print(f"\n===== {api_name.upper()} API RESPONSE =====")

    questions = result.get("questions_answered") or []

    if questions:
        print("Questions answered:")
        for index, question in enumerate(questions, start=1):
            print(f"{index}. {question}")

    if api_name == "ingest":
        print("Original rows:", result.get("original_rows"))
        print("Original columns:", result.get("original_columns"))
        print("Final rows:", result.get("rows_loaded"))
        print("Final columns:", result.get("columns_loaded"))
        print("Unique crime types:", result.get("unique_crime_types"))
    else:
        if isinstance(result.get("kpis"), dict):
            print("Key metrics:")
            for key, value in result["kpis"].items():
                print(f"- {key}: {value}")

    print("===== END API RESPONSE =====\n")


def enrich_api_response(result, api_name, label):
    result["api_name"] = api_name
    result["title"] = label
    result["purpose"] = (
        "Answer the business and analytics questions for the selected use case using cleaned Chicago crime data."
        if api_name == "analyse" else
        "Provide an overview of the dataset quality, crime activity, and overall analytical insights."
    )

    summary_text = result.get(
        "summary",
        "This response explains the analytical result in a business-friendly way and highlights the key insight from the dataset."
    )
    questions = result.get(
        "questions_answered",
        [
            "What is the main insight from this result?",
            "How does this answer the business objective?",
            "What should be done based on this analysis?"
        ]
    )

    result["summary"] = summary_text
    result["questions_answered"] = questions

    result["report"] = {
        "title": label,
        "api_name": api_name,
        "purpose": result["purpose"],
        "summary": summary_text,
        "questions_answered": questions,
        "key_findings": result.get(
            "key_findings",
            [summary_text]
        )
    }

    result["print_summary"] = "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(questions, start=1)
    )

    return result


@api.route("/api/status")
def status():

    return jsonify({
        "status": "success",
        "message": "Chicago Crime Analytics API is running"
    })


@api.route("/api/patrol-requests", methods=["GET"])
def list_patrol_requests():
    ensure_patrol_requests_table()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM patrol_requests ORDER BY request_id DESC"
    ).fetchall()
    conn.close()
    return jsonify([patrol_request_to_dict(row) for row in rows])


@api.route("/api/patrol-requests", methods=["POST"])
def create_patrol_request():
    cleaned, error = validate_patrol_payload(request.get_json(silent=True), partial=False)
    if error:
        return jsonify({"status": "error", "error": error}), 400

    ensure_patrol_requests_table()
    timestamp = patrol_timestamp()
    columns = list(cleaned) + ["requested_at", "updated_at"]
    values = [cleaned[column] for column in cleaned] + [timestamp, timestamp]
    placeholders = ", ".join("?" for _ in columns)

    conn = get_connection()
    cursor = conn.execute(
        f"INSERT INTO patrol_requests ({', '.join(columns)}) VALUES ({placeholders})",
        values
    )
    row = conn.execute(
        "SELECT * FROM patrol_requests WHERE request_id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.commit()
    conn.close()

    # Sync database changes to CSV file
    sync_patrol_requests_to_csv()

    return jsonify(patrol_request_to_dict(row)), 201


@api.route("/api/patrol-requests/<int:request_id>", methods=["GET"])
def get_patrol_request(request_id):
    ensure_patrol_requests_table()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM patrol_requests WHERE request_id = ?", (request_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return jsonify({"status": "error", "error": "Patrol request not found."}), 404
    return jsonify(patrol_request_to_dict(row))


@api.route("/api/patrol-requests/<int:request_id>", methods=["PUT"])
def update_patrol_request(request_id):
    cleaned, error = validate_patrol_payload(request.get_json(silent=True), partial=True)
    if error:
        return jsonify({"status": "error", "error": error}), 400
    if not cleaned:
        return jsonify({"status": "error", "error": "Provide at least one field to update."}), 400

    ensure_patrol_requests_table()
    assignments = [f"{column} = ?" for column in cleaned]
    values = list(cleaned.values())
    assignments.append("updated_at = ?")
    values.extend([patrol_timestamp(), request_id])

    conn = get_connection()
    cursor = conn.execute(
        f"UPDATE patrol_requests SET {', '.join(assignments)} WHERE request_id = ?", values
    )
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"status": "error", "error": "Patrol request not found."}), 404
    row = conn.execute(
        "SELECT * FROM patrol_requests WHERE request_id = ?", (request_id,)
    ).fetchone()
    conn.commit()
    conn.close()

    # Sync database changes to CSV file
    sync_patrol_requests_to_csv()

    return jsonify(patrol_request_to_dict(row))


@api.route("/api/patrol-requests/<int:request_id>", methods=["DELETE"])
def delete_patrol_request(request_id):
    ensure_patrol_requests_table()
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM patrol_requests WHERE request_id = ?", (request_id,)
    )
    conn.commit()
    conn.close()

    # Sync database changes to CSV file
    sync_patrol_requests_to_csv()

    return jsonify({
        "status": "success",
        "message": "Patrol request deleted successfully."
    })


@api.route("/api/ingest", methods=["GET", "POST"])
def ingest():

    try:

        result = ingest_data()
        result = enrich_api_response(result, "ingest", "Use Case 1 - Data Ingestion and Cleaning")
        print_api_result("ingest", result)

        return jsonify(result)

    except Exception as e:

        print("INGEST ERROR:", e)

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@api.route("/api/statistics")
def statistics():

    try:

        result = get_statistics()
        result = enrich_api_response(result, "statistics", "Chicago Crime Dashboard Summary")
        print_api_result("statistics", result)

        return jsonify(result)

    except Exception as e:

        print("STATISTICS ERROR:", e)

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@api.route("/api/analyse")
def analyse():

    case_number = request.args.get(
        "case"
    )

    try:

        case_number = int(
            case_number
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "status": "error",
            "error": "Invalid case number"
        }), 400

    try:

        if case_number == 1:

            result = (
                case1_crime_type_analysis()
            )
            title = "Use Case 1 - Crime Type Distribution"

        elif case_number == 2:

            result = (
                case2_arrest_analysis()
            )
            title = "Use Case 2 - Arrest Analysis"

        elif case_number == 3:

            result = (
                case3_time_analysis()
            )
            title = "Use Case 3 - Time and Pattern Analysis"

        elif case_number == 4:

            result = (
                case4_geographic_analysis()
            )
            title = "Use Case 4 - Geographic Hotspot Analysis"

        else:

            return jsonify({
                "status": "error",
                "error": "Case must be 1, 2, 3 or 4"
            }), 400

        result["case_number"] = case_number
        result = enrich_api_response(result, "analyse", title)
        print_api_result(f"analyse_case_{case_number}", result)

        return jsonify(result)

    except Exception as e:

        print(
            f"CASE {case_number} ERROR:",
            e
        )

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
