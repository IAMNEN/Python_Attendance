from pymongo import MongoClient
from datetime import datetime
import csv

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_system"]
employees_col = db["employees"]
attendance_col = db["attendance"]

def add_employee():
    name = input("Enter employee name: ").strip()
    if employees_col.find_one({"name": name}):
        print("⚠️ Employee already exists.")
        return
    employees_col.insert_one({"name": name})
    print(f"✅ {name} added successfully.")

def list_employees():
    employees = list(employees_col.find())
    if not employees:
        print("❌ No employees found.")
        return []
    print("\n📋 Employees:")
    for i, emp in enumerate(employees, 1):
        print(f"{i}. {emp['name']}")
    return employees

def mark_attendance():
    employees = list_employees()
    if not employees:
        return
    try:
        emp_id = int(input("Enter employee number: ")) - 1
        emp_name = employees[emp_id]['name']
    except (IndexError, ValueError):
        print("❌ Invalid input.")
        return

    print("\nMark for:", emp_name)
    print("1. Enter")
    print("2. Exit")
    print("3. Leave")
    choice = input("Enter choice (1/2/3): ")

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    existing_record = attendance_col.find_one({
        "name": emp_name,
        "date": date_str
    })

    if choice == '1':
        if existing_record and "enter_time" in existing_record:
            print("⚠️ Entry already marked.")
        else:
            if existing_record:
                attendance_col.update_one(
                    {"_id": existing_record["_id"]},
                    {"$set": {"enter_time": time_str, "status": "Present"}}
                )
            else:
                attendance_col.insert_one({
                    "name": emp_name,
                    "date": date_str,
                    "enter_time": time_str,
                    "status": "Present"
                })
            print(f"✅ Enter marked at {time_str}")

    elif choice == '2':
        if not existing_record:
            print("❌ Entry not found. Please mark entry first.")
        elif "exit_time" in existing_record:
            print("⚠️ Exit already marked.")
        else:
            attendance_col.update_one(
                {"_id": existing_record["_id"]},
                {"$set": {"exit_time": time_str}}
            )
            print(f"✅ Exit marked at {time_str}")

    elif choice == '3':
        if existing_record:
            print("⚠️ Attendance already exists for today.")
        else:
            reason = input("Enter leave reason: ")
            attendance_col.insert_one({
                "name": emp_name,
                "date": date_str,
                "status": "Leave",
                "reason": reason
            })
            print(f"✅ Leave marked with reason: {reason}")
    else:
        print("❗ Invalid choice.")

def view_attendance():
    records = list(attendance_col.find())
    if not records:
        print("❌ No records found.")
        return
    print("\n📝 Attendance Records:")
    print("Name\t\tDate\t\tEnter\t\tExit\t\tStatus\tReason")
    print("-" * 90)
    for rec in records:
        print(f"{rec.get('name', '')}\t{rec.get('date', '')}\t{rec.get('enter_time', '-')}\t{rec.get('exit_time', '-')}\t{rec.get('status', '-')}\t{rec.get('reason', '-')}")

def export_to_csv():
    records = list(attendance_col.find())
    if not records:
        print("❌ No data to export.")
        return

    filename = "attendance_export.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Date", "Enter Time", "Exit Time", "Status", "Reason"])
        for rec in records:
            writer.writerow([
                rec.get("name", ""),
                rec.get("date", ""),
                rec.get("enter_time", ""),
                rec.get("exit_time", ""),
                rec.get("status", ""),
                rec.get("reason", "")
            ])
    print(f"✅ Data exported to {filename}")

def main():
    while True:
        print("\n🎯 Employee Attendance System")
        print("1. Add Employee")
        print("2. Mark Attendance (Enter / Exit / Leave)")
        print("3. View Attendance")
        print("4. Export to CSV")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            add_employee()
        elif choice == '2':
            mark_attendance()
        elif choice == '3':
            view_attendance()
        elif choice == '4':
            export_to_csv()
        elif choice == '5':
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❗ Invalid choice. Please enter between 1 to 5.")

if __name__ == "__main__":
    main()
