from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Student Assistant MCP")


@mcp.tool()
def calculate_percentage(marks: float, total_marks: float) -> str:
    """Calculate a student's percentage."""
    if total_marks <= 0:
        return "Error: total_marks must be greater than 0."

    percentage = (marks / total_marks) * 100
    return f"Percentage: {percentage:.2f}%"


@mcp.tool()
def calculate_cgpa(
    total_grade_points: float,
    total_credit_hours: float
) -> str:
    """Calculate CGPA from total grade points and credit hours."""
    if total_credit_hours <= 0:
        return "Error: total_credit_hours must be greater than 0."

    cgpa = total_grade_points / total_credit_hours
    return f"CGPA: {cgpa:.2f}"


@mcp.tool()
def get_course_info(course: str) -> str:
    """Return information about common computer science courses."""

    courses = {
        "data communication":
            "Data Communication covers how data is transmitted between devices, including protocols, transmission media, and networking basics.",

        "computer networks":
            "Computer Networks covers communication between computers, network models, protocols, IP addressing, routing, and network security basics.",

        "database":
            "Database courses cover data storage, SQL, tables, relationships, normalization, and database management systems.",

        "artificial intelligence":
            "Artificial Intelligence covers techniques that allow computers to solve problems that normally require human intelligence.",

        "machine learning":
            "Machine Learning focuses on training models to learn patterns from data and make predictions or decisions.",
    }

    key = course.strip().lower()

    if key in courses:
        return f"{course}: {courses[key]}"

    return f"No stored information found for '{course}'."


if __name__ == "__main__":
    mcp.run()
