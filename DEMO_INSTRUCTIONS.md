# 🚀 AI Social Media Content Agent - Live Demo

## Quick Start (60 seconds to running demo)

### **1. Launch Demo (One Command)**
```bash
./start_demo.sh
```

### **2. View Dashboard**
Open your browser to: **http://localhost:5173**

### **3. Explore Features**
- ✅ **Professional Dashboard** - Real-time metrics and analytics
- ✅ **Content Management** - AI-powered content creation
- ✅ **Analytics Dashboard** - Performance tracking across platforms
- ✅ **Memory Explorer** - Semantic search and content intelligence
- ✅ **Goal Tracking** - Automated progress monitoring
- ✅ **Calendar View** - Content scheduling interface
- ✅ **Performance Dashboard** - Real-time system metrics

## 📱 What You'll See

### **Main Dashboard Features:**
- **4 Key Metric Cards** - Views, Engagement, Followers, Total Engagement
- **Autonomous Workflow Tracker** - Live workflow stage monitoring
- **Goal Progress Visualization** - Interactive progress bars
- **Memory System Statistics** - AI system analytics
- **Real-time Connection Status** - Live system health

### **Navigation Sections:**
1. **Overview** - Main dashboard home
2. **Calendar** - Content scheduling interface
3. **Analytics** - Performance metrics and charts
4. **Performance** - Real-time system dashboard
5. **Content** - Content management and creation
6. **Memory** - AI memory explorer with semantic search
7. **Goals** - Goal tracking and progress management
8. **Settings** - Configuration and preferences

## 🔧 Technical Details

### **Demo Configuration:**
- **Database:** SQLite (no PostgreSQL required)
- **Authentication:** Simplified demo auth (no Auth0 required)
- **Social Media APIs:** Mock data mode
- **Real-time Updates:** Simulated with sample data

### **System Requirements:**
- **Python 3.11+** with virtual environment
- **Node.js 20+** for frontend
- **Ports:** 8000 (backend), 5173 (frontend)

## 🛑 Stop Demo

### **Option 1: Use stop script**
```bash
./stop_demo.sh
```

### **Option 2: Manual cleanup**
```bash
# Kill processes
kill $(cat .backend_pid .frontend_pid)

# Clean up ports
lsof -ti:8000,5173 | xargs kill -9
```

## 🎯 Demo Highlights

### **Professional Enterprise Interface**
- Modern React 18 architecture
- Tailwind CSS styling
- Responsive mobile-first design
- Accessibility compliance (WCAG 2.1)
- Error boundaries and graceful degradation

### **Real-time Dashboard Features**
- Live metrics updates every 30 seconds
- Interactive charts and visualizations
- Professional color scheme and branding
- Loading states and skeleton screens
- Professional navigation with active states

### **AI-Powered Capabilities**
- Semantic memory system with vector search
- Automated workflow orchestration
- Content generation and optimization
- Multi-platform social media integration
- Performance analytics and insights

## 🚨 Troubleshooting

### **Port Already in Use**
```bash
# Check what's using the ports
lsof -i :8000 -i :5173

# Kill any conflicting processes
./stop_demo.sh
```

### **Dependencies Missing**
```bash
# Backend dependencies
source venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install
```

### **Database Issues**
```bash
# Remove and recreate database
rm socialmedia.db
./start_demo.sh
```

## 📊 Demo Data

The demo uses realistic sample data including:
- **150+ mock social media posts**
- **Performance metrics** across 5 platforms
- **Goal tracking** with progress visualization
- **Memory system** with content analytics
- **Real-time workflow** status updates

---

**🎉 Ready to see the AI Social Media Content Agent in action?**

**Run:** `./start_demo.sh`

**Visit:** http://localhost:5173

*Professional AI-powered social media management at your fingertips!*