# 💸 Expense Tracker MCP Server

This is a small local **Expense Tracker** built using **FastMCP** and **SQLite**, designed to connect with **Claude Desktop** as a local MCP (Model Context Protocol) server.

It allows you to **add, edit, delete, list, and search expenses**, as well as generate summaries and export data to CSV or JSON — all running locally on your machine.

---

## 🚀 Features

- Add new expenses with date, amount, category, and notes  
- List or search expenses by date or keyword  
- Edit or delete existing expenses  
- Generate monthly summaries by category  
- View basic statistics (total spent, average, count)  
- Export all data to CSV or JSON  
- Uses a local SQLite database (`expenses.db`)  
- Works directly with Claude Desktop MCP integration  

---

## 🧠 How It Works

The project runs as an **MCP server** using [FastMCP](https://gofastmcp.com/).  
Claude Desktop communicates with it via STDIO and can perform natural language commands like:

> “Add a $50 expense for food today.”  
> “Show me all travel expenses this week.”  
> “Export my expenses to CSV.”

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/expense-tracker-mcp.git
cd expense-tracker-mcp
```

### 2. Install dependencies
```bash
pip install fastmcp uv
```

### 3. Run the server manually
```bash
uv run fastmcp run main_v2.py
```

You should see something like:
```
🖥 Server name: ExpenseTracker
📦 Transport: STDIO
INFO Starting MCP server 'ExpenseTracker'
```

---

## 🧰 Claude Desktop Configuration

To connect the server to Claude Desktop:

1. Open your `claude-desktop-config.json` file  
2. Add this section:

```json
{
  "mcpServers": {
    "ExpenseTracker": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp",
        "run",
        "E:/Coding-Practice/MCP-local-server/main_v2.py"
      ],
      "transport": "stdio"
    }
  }
}
```

3. Restart Claude Desktop  
4. Go to **Settings → Developer → Local MCP servers** and confirm **ExpenseTracker** is running ✅

---

## 🧩 Tools Available

- `add_expense(date, amount, category, subcategory="", note="")` → Add new expense  
- `list_expenses(start_date, end_date)` → List expenses in a range  
- `edit_expense(id, ...)` → Update a record  
- `delete_expense(id)` → Delete a record  
- `search_expenses(keyword)` → Search by note/category/subcategory  
- `monthly_summary(year, month)` → Show total per category for a month  
- `get_statistics()` → Show total and average spending  
- `export_expenses(format="csv")` → Export data to CSV or JSON  

---

## 📁 Example Output

### Add Expense
```json
{ "status": "ok", "id": 5 }
```

### List Expenses
```json
[
  {
    "id": 1,
    "date": "2025-11-06",
    "amount": 12.5,
    "category": "Food",
    "subcategory": "Lunch",
    "note": "McDonald's"
  },
  {
    "id": 2,
    "date": "2025-11-07",
    "amount": 30,
    "category": "Travel",
    "subcategory": "",
    "note": "Uber ride"
  }
]
```

---

## 📘 Categories File

The `categories.json` file defines available categories, for example:
```json
["Food", "Travel", "Bills", "Entertainment", "Misc"]
```

You can edit this file anytime — the changes will apply instantly without restarting the server.

---

## 🧾 Summary

This project demonstrates how to integrate a **local FastMCP server** with **Claude Desktop** to manage personal data — in this case, expenses.  
It’s a lightweight, local-first solution that combines simple data storage with AI-powered interaction.
