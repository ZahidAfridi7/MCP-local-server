from fastmcp import FastMCP
import os
import sqlite3
import json
import csv
from datetime import datetime

# === Paths ===
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "expenses.db")
CATEGORIES_PATH = os.path.join(BASE_DIR, "categories.json")

# === MCP Server ===
mcp = FastMCP("ExpenseTracker")

# === Database Initialization ===
def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
init_db()

# === CRUD TOOLS ===

@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool()
def list_expenses(start_date=None, end_date=None):
    """List all expenses or those within a given date range."""
    with sqlite3.connect(DB_PATH) as c:
        query = "SELECT id, date, amount, category, subcategory, note FROM expenses"
        params = ()
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params = (start_date, end_date)
        query += " ORDER BY date ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def edit_expense(id, date=None, amount=None, category=None, subcategory=None, note=None):
    """Edit an existing expense record."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT * FROM expenses WHERE id=?", (id,))
        row = cur.fetchone()
        if not row:
            return {"status": "error", "message": f"Expense with id {id} not found"}

        updates = []
        params = []
        for field, value in [
            ("date", date),
            ("amount", amount),
            ("category", category),
            ("subcategory", subcategory),
            ("note", note)
        ]:
            if value is not None:
                updates.append(f"{field} = ?")
                params.append(value)

        if not updates:
            return {"status": "no_changes"}

        params.append(id)
        c.execute(f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?", params)
        return {"status": "ok", "updated_fields": updates}


@mcp.tool()
def delete_expense(id):
    """Delete an expense entry by ID."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("DELETE FROM expenses WHERE id=?", (id,))
        if cur.rowcount == 0:
            return {"status": "error", "message": f"Expense with id {id} not found"}
        return {"status": "ok", "deleted_id": id}


# === EXTRA TOOLS ===

@mcp.tool()
def search_expenses(keyword):
    """Search expenses by keyword in category, subcategory, or note."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("""
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE category LIKE ? OR subcategory LIKE ? OR note LIKE ?
            ORDER BY date DESC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def monthly_summary(year, month):
    """Summarize total spending by category for a given month."""
    start = f"{year}-{month:02d}-01"
    end = f"{year}-{month:02d}-31"
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("""
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY category ASC
        """, (start, end))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def get_statistics():
    """Return basic statistics about all recorded expenses."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT COUNT(*), SUM(amount), AVG(amount) FROM expenses")
        count, total, avg = cur.fetchone()
        return {
            "total_entries": count or 0,
            "total_spent": total or 0.0,
            "average_expense": avg or 0.0
        }


@mcp.tool()
def export_expenses(format="csv"):
    """Export all expenses to a CSV or JSON file in the same directory."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT * FROM expenses ORDER BY date ASC")
        cols = [d[0] for d in cur.description]
        data = [dict(zip(cols, r)) for r in cur.fetchall()]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format.lower() == "json":
        file_path = os.path.join(BASE_DIR, f"export_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    else:
        file_path = os.path.join(BASE_DIR, f"export_{timestamp}.csv")
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(data)

    return {"status": "ok", "exported_file": file_path}


# === Resource ===

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    """Return the current categories list from categories.json"""
    if not os.path.exists(CATEGORIES_PATH):
        return json.dumps(["Food", "Travel", "Bills", "Entertainment", "Misc"])
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


# === Entry point ===
if __name__ == "__main__":
    mcp.run()
