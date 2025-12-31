# 🎨 SkillAlign Frontend

> **The Visual Interface for the SkillAlign Intelligence Engine**

This is the Next.js frontend for SkillAlign, designed to provide a seamless, interactive, and semantically rich user experience for career discovery and skill-gap analysis.

---

## ✨ Features

- **⚡ Reactive Performance**: Built on **Next.js 14** and **React 18** for server-side rendering and static generation.
- **🧠 Intelligent Search**: Real-time checking of skill embeddings powered by **React Query (TanStack Query)**.
- **🎨 Modern UI/UX**: A fully responsive, dark-mode native interface using **Tailwind CSS** and **Lucide Icons**.
- **♿ Accessible Design**: Utilizes **Radix UI** primitives to ensuring high accessibility standards.
- **🧩 Component Architecture**: Modular component system for scalable development and maintenance.

---

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Framework** | `Next.js 14` | Core React framework with App Router |
| **Language** | `TypeScript` | Strict type safety across the application |
| **Styling** | `Tailwind CSS 3.4` | Utility-first CSS framework |
| **UI Primitives** | `Radix UI` | Unstyled, accessible component library |
| **State/Query** | `TanStack Query` | Server state management & caching |
| **Icons** | `Lucide React` | Clean, consistent SVG icons |
| **Validation** | `Zod` | Schema validation for user inputs |

---

## 📂 Project Structure

```bash
app/frontend/
├── app/                  # App Router pages and layouts
│   ├── (admin)/          # Admin dashboard routes
│   └── (public)/         # Public-facing user routes
├── components/           # Reusable UI components
│   ├── features/         # Feature-specific components (recommendations, etc.)
│   ├── layout/           # Global layout components (sidebar, navbar)
│   └── ui/               # Generic UI primitives (buttons, inputs)
├── lib/                  # Utility functions and shared helpers
├── services/             # API integration services (Axios)
└── types/                # TypeScript type definitions
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+**
- **npm** or **yarn**

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd app/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open in Browser:**
   Visit [http://localhost:3000](http://localhost:3000) to see the application.

---

## 🔧 Scripts

- `npm run dev`: Starts the development server.
- `npm run build`: Builds the application for production.
- `npm start`: Runs the built production application.
- `npm run lint`: Runs ESLint for code quality checks.

---

*Part of the SkillAlign ecosystem.*
