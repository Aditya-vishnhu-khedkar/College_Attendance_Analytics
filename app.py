from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# =========================================================
# LOAD CSV
# =========================================================

df = pd.read_csv("attendance.csv")

# Clean column names
df.columns = df.columns.str.strip()


# =========================================================
# CONVERT NUMERIC COLUMNS
# =========================================================

df["attendance"] = pd.to_numeric(
    df["attendance"],
    errors="coerce"
)

df["study_hours"] = pd.to_numeric(
    df["study_hours"],
    errors="coerce"
)

df["sleep_hours"] = pd.to_numeric(
    df["sleep_hours"],
    errors="coerce"
)

df["travel_time_minutes"] = pd.to_numeric(
    df["travel_time_minutes"],
    errors="coerce"
)


# Remove invalid attendance records
df = df.dropna(
    subset=["attendance"]
)


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    # -----------------------------------------------------
    # GET FILTER VALUES
    # -----------------------------------------------------

    selected_course = request.args.get(
        "course",
        ""
    )

    selected_year = request.args.get(
        "year",
        ""
    )

    selected_gender = request.args.get(
        "gender",
        ""
    )

    selected_class = request.args.get(
        "class_type",
        ""
    )

    selected_hostel = request.args.get(
        "hostel_resident",
        ""
    )

    selected_internet = request.args.get(
        "internet_access",
        ""
    )

    search = request.args.get(
        "search",
        ""
    )

    attendance_filter = request.args.get(
        "attendance_filter",
        ""
    )


    # =====================================================
    # FILTER DATA
    # =====================================================

    filtered_df = df.copy()


    # Course

    if selected_course:

        filtered_df = filtered_df[
            filtered_df["course"].astype(str)
            == selected_course
        ]


    # Year

    if selected_year:

        filtered_df = filtered_df[
            filtered_df["year"].astype(str)
            == selected_year
        ]


    # Gender

    if selected_gender:

        filtered_df = filtered_df[
            filtered_df["gender"].astype(str)
            == selected_gender
        ]


    # Class Type

    if selected_class:

        filtered_df = filtered_df[
            filtered_df["class_type"].astype(str)
            == selected_class
        ]


    # Hostel

    if selected_hostel:

        filtered_df = filtered_df[
            filtered_df["hostel_resident"].astype(str)
            == selected_hostel
        ]


    # Internet

    if selected_internet:

        filtered_df = filtered_df[
            filtered_df["internet_access"].astype(str)
            == selected_internet
        ]


    # Search student ID

    if search:

        filtered_df = filtered_df[
            filtered_df["student_id"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    # Attendance filter

    if attendance_filter == "high":

        filtered_df = filtered_df[
            filtered_df["attendance"] >= 75
        ]

    elif attendance_filter == "medium":

        filtered_df = filtered_df[
            (filtered_df["attendance"] >= 50)
            &
            (filtered_df["attendance"] < 75)
        ]

    elif attendance_filter == "low":

        filtered_df = filtered_df[
            filtered_df["attendance"] < 50
        ]


    # =====================================================
    # KPI
    # =====================================================

    total_students = filtered_df[
        "student_id"
    ].nunique()


    if len(filtered_df) > 0:

        average_attendance = round(
            filtered_df["attendance"].mean(),
            2
        )

        average_study_hours = round(
            filtered_df["study_hours"].mean(),
            2
        )

        average_sleep_hours = round(
            filtered_df["sleep_hours"].mean(),
            2
        )

    else:

        average_attendance = 0
        average_study_hours = 0
        average_sleep_hours = 0


    # =====================================================
    # COURSE DATA
    # =====================================================

    course_data = (
        filtered_df
        .groupby("course")["attendance"]
        .mean()
        .round(2)
        .reset_index()
    )


    # =====================================================
    # YEAR DATA
    # =====================================================

    year_data = (
        filtered_df
        .groupby("year")["attendance"]
        .mean()
        .round(2)
        .reset_index()
    )


    # =====================================================
    # GENDER DATA
    # =====================================================

    gender_data = (
        filtered_df
        .groupby("gender")["attendance"]
        .mean()
        .round(2)
        .reset_index()
    )


    # =====================================================
    # CLASS TYPE
    # =====================================================

    class_data = (
        filtered_df
        .groupby("class_type")["attendance"]
        .mean()
        .round(2)
        .reset_index()
    )


    # =====================================================
    # HOSTEL
    # =====================================================

    hostel_data = (
        filtered_df
        .groupby("hostel_resident")["attendance"]
        .mean()
        .round(2)
        .reset_index()
    )


    # =====================================================
    # INTERNET
    # =====================================================

    internet_data = (
        filtered_df
        .groupby("internet_access")["attendance"]
        .mean()
        .round(2)
        .reset_index()
    )


    # =====================================================
    # ABSENCE REASONS
    # =====================================================

    absence_data = (
        filtered_df["absence_reason"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    absence_data.columns = [
        "reason",
        "count"
    ]


    # =====================================================
    # STUDY HOURS
    # =====================================================

    study_data = (
        filtered_df
        .groupby("study_hours")["attendance"]
        .mean()
        .round(2)
        .reset_index()
        .sort_values("study_hours")
    )


    # =====================================================
    # STUDENT TABLE
    # =====================================================

    student_table = filtered_df[
        [
            "student_id",
            "age",
            "gender",
            "course",
            "year",
            "class_type",
            "study_hours",
            "sleep_hours",
            "attendance",
            "absence_reason"
        ]
    ].copy()


    # Limit table records
    student_table = student_table.head(100)


    # Convert to dictionary
    student_records = student_table.to_dict(
        orient="records"
    )


    # =====================================================
    # FILTER OPTIONS
    # =====================================================

    courses = sorted(
        df["course"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    years = sorted(
        df["year"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    genders = sorted(
        df["gender"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    class_types = sorted(
        df["class_type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    hostel_options = sorted(
        df["hostel_resident"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    internet_options = sorted(
        df["internet_access"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(

        "index.html",

        # KPI
        total_students=total_students,
        average_attendance=average_attendance,
        average_study_hours=average_study_hours,
        average_sleep_hours=average_sleep_hours,

        # Charts
        course_names=course_data["course"].tolist(),
        course_values=course_data["attendance"].tolist(),

        year_names=year_data["year"].astype(str).tolist(),
        year_values=year_data["attendance"].tolist(),

        gender_names=gender_data["gender"].astype(str).tolist(),
        gender_values=gender_data["attendance"].tolist(),

        class_names=class_data["class_type"].astype(str).tolist(),
        class_values=class_data["attendance"].tolist(),

        hostel_names=hostel_data["hostel_resident"].astype(str).tolist(),
        hostel_values=hostel_data["attendance"].tolist(),

        internet_names=internet_data["internet_access"].astype(str).tolist(),
        internet_values=internet_data["attendance"].tolist(),

        absence_names=absence_data["reason"].astype(str).tolist(),
        absence_values=absence_data["count"].tolist(),

        study_hours=study_data["study_hours"].tolist(),
        study_attendance=study_data["attendance"].tolist(),

        # Student table
        student_records=student_records,

        # Filter options
        courses=courses,
        years=years,
        genders=genders,
        class_types=class_types,
        hostel_options=hostel_options,
        internet_options=internet_options,

        # Selected filters
        selected_course=selected_course,
        selected_year=selected_year,
        selected_gender=selected_gender,
        selected_class=selected_class,
        selected_hostel=selected_hostel,
        selected_internet=selected_internet,
        search=search,
        attendance_filter=attendance_filter
    )


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)