# ClawReceipt 🧾

**เก็บใบเสร็จอัตโนมัติ สำหรับ OpenClaw**

เครื่องมือตัวช่วยสำหรับจัดการใบเสร็จ ข้อมูลการใช้จ่าย และแจ้งเตือน Budget ถูกออกแบบมาเพื่อทำงานร่วมกับ AI Agent (OpenClaw) โดยเฉพาะ ด้วยระบบหน้าบ้านแบบ CLI/TUI ที่ตกแต่งสไตล์ Retro Neon สุดเท่ (ClawFlow)

## 📌 Features

- **Data Extractor Ready**: ส่งรูปแบบพารามิเตอร์มารับจบ บันทึกข้อมูล (วัน/เวลา/ร้าน/ยอดเงิน/หมวดหมู่)
- **Auto Budget Alert**: ตั้ง Budget รายเดือน ถ้ายอดบิลใช้จ่ายไหนทะลุงบระบบจะแจ้งเตือน `Exceeded Budget!` ทันที
- **Terminal UI (TUI)**: แดชบอร์ดสำหรับเรียกดูใบเสร็จย้อนหลังแบบตารางสวยงาม
- **Exporters**: สั่ง Export เป็น `CSV` และ `Excel` สำหรับส่งให้ฝ่ายบัญชีใช้งานต่อ
- **OpenClaw Skill Compliant**: มาพร้อมไฟล์ `SKILL.md` รูปแบบมาตรฐานสำหรับให้ OpenClaw Agent โหลดโมดูลเข้าไปใช้งาน

## 📂 Project Structure

```text
ClawReceipt/
├── data/                    # โฟลเดอร์เก็บฐานข้อมูล SQLite อัตโนมัติ (receipts.db)
├── src/                     # โค้ด Backend และ Logic ของโปรเจกต์
│   ├── cli.py               # โค้ดรับคำสั่ง CLI
│   ├── db.py                # ระบบติดต่อ Database SQLite
│   ├── styling.py           # ระบบตกแต่งสีสัน Terminal UI (Rich)
│   └── tui.py               # หน้าจอ Visual Terminal Interface
├── SKILL.md                 # 🔑 คู่มือ OpenClaw สำหรับให้ AI เรียกใช้ Tool นี้
├── requirements.txt         # ไฟล์รวม Packages Dependencies
└── run.py                   # 🚀 ตัวรันโปรแกรมหลัก (Entry Point)
```

## 🛠️ Installation & Setup

1. **สร้างและรัน Virtual Environment:**

```bash
python -m venv venv
.\venv\Scripts\activate   # สำหรับ Windows
```

2. **ติดตั้ง Dependency:**

```bash
pip install -r requirements.txt
```

## 🚀 Usage Guide

ทุกคำสั่งให้เรียกผ่าน `run.py`

### 1. บันทึกใบเสร็จ (สำหรับ OpenClaw ใช้ยิงข้อมูล)

```bash
python run.py add --date "2026-02-27" --time "15:30:00" --store "Seven Eleven" --amount 120.50 --category "อาหาร"
```

### 2. ตั้งค่างบประมาณ / ตรวจเช็ค Budget

```bash
# กำหนด Budget 
python run.py budget --set 5000

# เช็คยอดใช้จ่ายรวมปัจจุบัน 
python run.py budget
```

### 3. ดูตารางใบเสร็จทั้งหมด (CLI Format)

```bash
python run.py list
```

### 4. เปิดหน้า Dashboard TUI สุดหรู (แบบมี UI)

```bash
python run.py tui
```

> ในหน้านี้สามารถกดปุ่ม **Export CSV** หรือ **Export Excel** ได้เลย

## 🤖 สำหรับ OpenClaw Agent

- ตรวจสอบ `SKILL.md` สำหรับคู่มือในการใช้งานโมดูล
- การใช้คำสั่งในฐานะ AI ห้ามเรียกใช้เข้าโหมด `tui` เพราะตัวคำสั่งจะล็อก Shell ของคุณ
