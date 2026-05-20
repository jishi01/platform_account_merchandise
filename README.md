# Platform Account Merchandise 🛒
### Cloud-Based Secure Digital Account Marketplace
> **A secure, centralized, and reliable full-stack marketplace application featuring an automated administrator verification pipeline, an integrated MySQL transaction database, and an isolated infrastructure staging environment.**

Developed as a final project for **CpEE 401 – Cognate/Elective Course 1** **CpE 2205 | Batangas State University | May 2026**

---

## 📌 Overview
The rapid growth of online gaming and digital services has created a high-volume marketplace for trading premium gaming accounts (e.g., *Mobile Legends: Bang Bang*, *Call of Duty: Mobile*) and established social media channels (*Facebook*, *TikTok*). However, informal trading over unverified social networks exposes students and digital consumers to serious risks of financial scams, identity theft, fake seller metrics, and fraudulent account recoveries.

**Platform Account Merchandise** solves this problem by delivering a dedicated, organized marketplace web application. It guarantees transaction safety, seller accountability, and data integrity through structured admin approval gates, transactional locking, and systematic receipt tracking.

### Core Capabilities:
* **Two-Way Marketplace Routing:** Enables authenticated users to securely register, list their digital account assets with targeted metadata, or browse and purchase verified offerings.
* **Admin Verification Gate:** Submitted listings are placed into a restricted `PENDING` state until an administrator validates the asset metrics, filtering out fraudulent listings before they hit the live store feed.
* **Automated Asset Handover:** Upon completing a simulated GCash payment processing cycle, the application instantly updates ownership, removes the listing from public view, and delivers an immediate transaction receipt containing the login credentials.
* **Relational Security Architecture:** Connects sellers directly to their created products using strict foreign key constraints in a MySQL backend.

---

## ✨ Features
* 🔐 **Secure Session Management** – Native Flask session tracking tied to cryptographic signed keys to handle state isolation securely over stateful client sessions.
* 🛡️ **Role-Based Access Control (RBAC)** – Rigid privilege separation separating standard buyers/sellers from critical dashboard administrative functions.
* 📋 **Admin Moderation Interface** – Dedicated backend workspace handling real-time state synchronization (`PENDING` ➔ `APPROVED` ➔ `SOLD`) for incoming listings.
* 💳 **Integrated Gateway Validation** – Robust client-side validation logic monitoring mobile formats alongside strict structural constraints on price and string entries.
* 🗂️ **Categorized Asset Management** – Clean asset sorting filtering across varied categories (Gaming, Social Media) coupled with managed persistent file uploads for promotional imagery.
* 🔒 **SQL Injection Defense** – Comprehensive adoption of parameterized database queries (`%s` placeholders) across all data-layer queries to neutralize security exploits.
* ⚡ **Performance Lifecycle Controls** – Efficient database lifecycle processing utilizing an aggressive `Open-Execute-Close` connection model to eliminate connection or socket exhaustion.

---

## 🛠️ Tech Stack

| Layer | Technology | Operational Context |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Responsive Presentation & Form Validation |
| **Template Engine** | Jinja2 | Dynamic Server-Side Rendering & Secure Context Injection |
| **Backend** | Python 3.11+, Flask | Central Route Controlling, Request Handlers, & Core App Logic |
| **Web Gateway Server** | Werkzeug WSGI | HTTP Parsing, Core Route Routing, & Path Sanitization |
| **Database Engine** | MySQL 8.0 (`platform_db`) | Relational Asset Tables, User Profiles, & Relational Constraints |
| **Virtualization / OS** | Oracle VirtualBox + Ubuntu Linux | Isolated Testing Server Environment (IaaS Deployment) |
| **Service Control** | systemd Daemon Unit | Background Application Lifecycle Management & Crash Recovery |
| **Network Protection** | UFW (Uncomplicated Firewall) | Production Port Isolation & Network Traffic Control Rules |

---

## 🗄️ Database Schema

### 1. `users` Table
Stores authentication credentials, user monikers, and access permission privileges.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` **(PK)** | INT | Auto-incrementing user primary identifier key. |
| `username` | VARCHAR(100) | Unique identification username handle. |
| `password` | VARCHAR(100) | Account protection authentication password. |
| `rrole` | VARCHAR(100) | Privilege configuration string (`admin`, `seller`, `buyer`). |

### 2. `platforms` Table
Tracks comprehensive transaction properties, visibility flags, and structural metadata for items.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` **(PK)** | INT | Auto-incrementing primary identifier for the listing. |
| `seller_id` **(FK)** | INT | Relational link mapping to `users(id)`. |
| `category` | VARCHAR(100) | Structural category group *(e.g., Mobile Legends, Facebook)*. |
| `title` | VARCHAR(100) | Human-readable header title summarizing the asset. |
| `details` | TEXT | Open-ended text field documenting skins, ranks, or metrics. |
| `price` | DECIMAL(10,2) | Verified cost metrics checked for mathematical structure. |
| `acc_email` | VARCHAR(100) | Stored asset username/email (Released post-payment only). |
| `acc_password` | VARCHAR(100) | Stored asset password credential (Released post-payment only). |
| `image_url` | VARCHAR(255) | Absolute storage reference pointing to the file image path. |
| `status` | VARCHAR(50) | State machine parameter (`PENDING`, `APPROVED`, `SOLD`). |

---

## 🚀 Getting Started

### Quick Deployment Summary
1. Provision an **Ubuntu Server 22.04 LTS** instance inside Oracle VirtualBox using **Bridged Networking**.
2. Configure core modules: install **Python 3**, **MySQL-Server**, **Git**, and **UFW** utilities.
3. Isolate application deployment parameters utilizing an active Python virtual environment (`venv`).
4. Establish database schema rulesets inside MySQL by generating the custom database instance `platform_db`.
5. Register a specialized systemd configuration wrapper (`market.service`) to handle 24/7 background availability.
6. Enforce production network rules using **UFW firewall** configurations.
7. Access the application runtime landing interface using: `http://<your-vm-ip>:5001/login`

---

## 🔒 Security Highlights
* **Privilege Separation:** Access controls isolate administration views from public users, preventing endpoint parameter tampering.
* **Injection Defense Engine:** Zero string concatenation used during backend calculations; queries are isolated using explicit parameterized structures.
* **Filename Sanitization:** Target upload storage vectors run through `secure_filename()` to combat file system directory traversal exploits.
* **Firewall Isolation Policies:** Core external request layers are monitored by UFW configuration profiles set to block unauthorized socket queries.

---

## 📁 Project Structure
```text
platform_account_merchandise/
├── app.py                 # Core application configuration, endpoint mapping, and control logic
├── static/                # Client-accessible static directory tree
│   ├── css/               # Application structure presentation styling rules
│   └── uploads/           # Persistent repository housing merchandise uploaded imagery
├── templates/             # Jinja2 presentation layouts executed on the server
│   ├── index.html         # Main dashboard displaying authenticated store listings
│   ├── admin.html         # Moderation workflow window displaying pending data fields
│   ├── login.html         # Verification view handling application profile matching
│   ├── checkout.html      # Secure checkout portal checking phone and pricing models
│   └── receipt.html       # Automated checkout statement delivering account credentials
├── market.service         # systemd automation control layer setup script
└── README.md              # System architecture setup instructions and guide
