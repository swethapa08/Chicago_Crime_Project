from flask import Flask, redirect, render_template, send_from_directory
from app.config import Config

from app.routes import api
from app.reporting import create_reporting_tables, generate_report_files
from app.visualization import create_all_visualizations


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.register_blueprint(api)


@app.route("/charts/<path:filename>")
def chart_file(filename):
    """Expose the reproducible Matplotlib/Seaborn output in the dashboard."""
    return send_from_directory(Config.CHARTS_DIR, filename)


@app.route("/reports/<path:filename>")
def report_file(filename):
    """Expose the generated CSV report files for download."""
    return send_from_directory(Config.REPORTS_DIR, filename)


def bootstrap_outputs():
    try:
        create_reporting_tables()
        generate_report_files()
        create_all_visualizations()
        print("\n=== OUTPUT GENERATION COMPLETE ===")
    except Exception as exc:
        print(f"Output generation skipped: {exc}")


@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html"
    )


@app.route("/case1")
def case1():

    return render_template(
        "case1.html"
    )


@app.route("/case2")
def case2():

    return render_template(
        "case2.html"
    )


@app.route("/case3")
def case3():

    return render_template(
        "case3.html"
    )


@app.route("/case4")
def case4():

    return render_template(
        "case4.html"
    )


@app.route("/reports")
def reports_page():
    return render_template("reports.html", active_page="reports")


@app.route("/patrol-requests")
def patrol_requests():
    return render_template("patrol_requests.html", active_page="patrol_requests")


@app.route("/crime-records")
def crime_records():
    return redirect("/patrol-requests", code=302)


if __name__ == "__main__":

    bootstrap_outputs()

    app.run(
        debug=True
    )
