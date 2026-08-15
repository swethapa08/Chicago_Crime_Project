from flask import Flask, redirect, render_template, send_from_directory

from .config import Config


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    from .routes import api

    app.register_blueprint(api)

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/case1")
    def case1():
        return render_template("case1.html")

    @app.route("/case2")
    def case2():
        return render_template("case2.html")

    @app.route("/case3")
    def case3():
        return render_template("case3.html")

    @app.route("/case4")
    def case4():
        return render_template("case4.html")

    @app.route("/reports")
    def reports_page():
        return render_template("reports.html", active_page="reports")

    @app.route("/patrol-requests")
    def patrol_requests():
        return render_template("patrol_requests.html", active_page="patrol_requests")

    @app.route("/crime-records")
    def crime_records():
        return redirect("/patrol-requests", code=302)

    @app.route("/charts/<path:filename>")
    def chart_file(filename):
        return send_from_directory(Config.CHARTS_DIR, filename)

    @app.route("/reports/<path:filename>")
    def report_file(filename):
        return send_from_directory(Config.REPORTS_DIR, filename)

    return app


app = create_app()