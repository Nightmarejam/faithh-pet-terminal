# FAITHH Journey Dashboard

A mission-control style visualization dashboard that interprets your 5-year FAITHH journey based on chat export archives and project state data.

## 🚀 Quick Start

```bash
# Start the dashboard
./scripts/start_dashboard.sh
```

This will:
- Launch the dashboard server on port 8080
- Process your chat archives to generate visualization data
- Open the dashboard in your browser
- Auto-refresh every 5 minutes

## 📊 Dashboard Features

### **Phase Timeline**
- Visual journey from Foundation through Legacy phases
- Current position indicator (Phase 2: Infrastructure)
- 5-year strategic overview

### **Domain Progress Rings**
- **Technical (FAITHH)**: Backend development, RAG pipeline, ML chips
- **Business (Tom Cat Sound)**: Revenue growth, client systems
- **Civic (Constella)**: Governance framework, community implementation
- **Personal (Mexico/Permaculture)**: Life integration, Spanish learning

### **Activity Heatmap**
- 6-month build activity pattern from chat archives
- Intensity visualization showing development focus
- Weekly/daily granularity

### **Milestone Timeline**
- Key achievements extracted from chat history
- Chronological progress tracking
- Cross-domain synergy indicators

### **Live Data Integration**
- Real-time connection to FAITHH backend
- Chat archive analysis
- Project state synchronization

## 🔧 Technical Architecture

### **Data Pipeline**
```
Chat Exports → Python Processor → JSON API → D3.js Visualizations
```

### **Key Components**
- `scripts/process_chat_exports.py` - Analyzes chat archives for patterns
- `scripts/dashboard_server.py` - HTTP server with API endpoints
- `faithh_journey_dashboard.html` - Mission-control UI with D3.js
- `dashboard_data.json` - Processed visualization data

### **API Endpoints**
- `/dashboard_data.json` - Main visualization data
- `/refresh` - Regenerate data from chat archives
- Static file serving for the HTML dashboard

## 📈 Data Sources

### **Chat Archives**
- `AI_Chat_Exports/all_recent_convos.json` - 78,689 lines of history
- `AI_Chat_Exports/recent_faithh_convos.json` - FAITHH-specific conversations
- Domain classification by keyword analysis
- Timeline extraction and activity intensity calculation

### **Project States**
- `project_states.json` - Current milestones and progress
- `faithh_memory.json` - Strategic context and 5-year plan
- Live FAITHH backend integration via `/health` endpoint

### **Strategic Framework**
- 5-year strategic plan integration
- Cross-domain synergy detection
- Resource allocation vs targets tracking

## 🎨 Mission-Control Aesthetic

The dashboard uses a dark, infrastructure-grade design inspired by mission control systems:

- **Color Scheme**: Cyan, orange, green, purple accents on dark background
- **Typography**: Space Mono monospace + Syne display fonts
- **Animations**: Scanning lines, pulsing indicators, smooth transitions
- **Layout**: Grid-based card system with clear visual hierarchy

## 🔄 Auto-Refresh & Updates

- **Auto-refresh**: Every 5 minutes
- **Manual refresh**: Call `/refresh` endpoint
- **Live data**: Integrates with FAITHH backend health status
- **Timestamp tracking**: Shows last update time

## 🛠️ Customization

### **Adding New Domains**
Edit `DOMAIN_KEYWORDS` in `process_chat_exports.py`:
```python
DOMAIN_KEYWORDS = {
    'new_domain': {
        'keywords': ['keyword1', 'keyword2'],
        'projects': ['Project Name']
    }
}
```

### **Modifying Visualizations**
- Edit `faithh_journey_dashboard.html` for UI changes
- Modify D3.js code for custom visualizations
- Update CSS variables for theme changes

### **Extending Data Sources**
- Add new data processors in `process_chat_exports.py`
- Extend dashboard data schema
- Update visualization components

## 📱 Browser Compatibility

- Chrome/Chromium: Full support
- Firefox: Full support
- Safari: Basic support
- Mobile: Responsive design included

## 🔍 Troubleshooting

### **Server Won't Start**
```bash
# Check if port 8080 is in use
lsof -i :8080

# Kill existing server
pkill -f dashboard_server.py
```

### **No Data Loading**
```bash
# Regenerate dashboard data
curl http://localhost:8080/refresh

# Check chat export files
ls -la AI_Chat_Exports/
```

### **Visualizations Not Updating**
- Check browser console for JavaScript errors
- Verify dashboard_data.json is being generated
- Check API endpoint responses

## 🚀 Future Enhancements

### **Phase 2: Advanced Features**
- Real-time FAITHH integration for live metrics
- Interactive timeline with drill-down capabilities
- Cross-domain synergy network visualization
- Predictive progress modeling

### **Phase 3: Integration**
- VS Code extension integration
- Automated insights generation
- Mobile app companion
- Export capabilities (PDF, PNG)

## 📞 Support

The dashboard is part of the FAITHH ecosystem. For issues:
1. Check this README for troubleshooting
2. Review the server logs in the terminal
3. Verify chat export data integrity
4. Check FAITHH backend connectivity

---

*"I see the whole gestalt and the path remains clear, even as I walk it differently than I first imagined."* - FAITHH Strategic Planning System, 2026
