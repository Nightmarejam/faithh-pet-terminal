# Compass System Hardening Plan
**Date:** 2026-02-19  
**Purpose**: Improve reliability, accuracy, and usefulness of the Compass/Compass Director system

---

## Current State Analysis

### What's Working ✅
- Health collector runs every 15 minutes (reliable)
- Director produces actionable intelligence
- UI displays system status correctly
- Basic collector framework is solid

### Issues Identified ⚠️
1. **Stale collectors**: git/file collectors only run every 4 hours, causing stale data
2. **Terminal collector**: 75 hours stale (not running properly)
3. **No error handling**: Collectors fail silently
4. **Limited visibility**: No monitoring of collector health
5. **Deprecation warnings**: Using deprecated datetime functions

---

## Hardening Initiatives

### 1. Collector Reliability (Priority: High)

#### Problem
- git/file collectors run every 4 hours → data appears stale
- terminal collector not running at all
- No retry logic for failed collectors

#### Solution
```python
# Enhanced collector runner with retry logic
class CollectorRunner:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 60  # seconds
    
    def run_with_retry(self, collector):
        for attempt in range(self.max_retries):
            try:
                result = collector.run()
                if result.get("success"):
                    return result
                else:
                    log_warning(f"Collector {collector.name} failed: {result.get('error')}")
            except Exception as e:
                log_error(f"Collector {collector.name} exception: {e}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return {"success": False, "error": f"Failed after {self.max_retries} attempts"}
```

#### Actions
- [ ] Add retry logic to all collectors
- [ ] Implement exponential backoff
- [ ] Add collector health monitoring
- [ ] Create collector status dashboard

### 2. Optimal Collection Intervals (Priority: High)

#### Current Intervals
- Health: 15 minutes ✅ (good)
- Git: 4 hours ❌ (too long for active development)
- Files: 4 hours ❌ (too long for active development)
- Terminal: 2 days ❌ (not running)

#### Proposed Intervals
```python
collection_intervals = {
    "health": timedelta(minutes=15),      # Keep as-is
    "git": timedelta(minutes=30),        # During active dev hours
    "file_changes": timedelta(minutes=30), # During active dev hours
    "terminal": timedelta(hours=1),     # Reduced from 2 days
}
```

#### Smart Scheduling
```python
def is_active_development_hours():
    """Check if we're in active development window (9 AM - 11 PM)"""
    hour = datetime.now().hour
    return 9 <= hour <= 23

def get_dynamic_interval(collector_name):
    """Adjust intervals based on activity"""
    base_intervals = {
        "git": timedelta(hours=4),
        "file_changes": timedelta(hours=4),
        "terminal": timedelta(hours=1),
    }
    
    if is_active_development_hours() and collector_name in ["git", "file_changes"]:
        return timedelta(minutes=30)
    
    return base_intervals.get(collector_name, timedelta(hours=1))
```

### 3. Enhanced Error Handling (Priority: Medium)

#### Current Issues
- Collectors fail silently
- No error aggregation
- No alerting for critical failures

#### Solution
```python
class CollectorError(Exception):
    def __init__(self, collector_name, error, severity="medium"):
        self.collector_name = collector_name
        self.error = error
        self.severity = severity
        self.timestamp = datetime.now(timezone.utc)

class ErrorAggregator:
    def __init__(self):
        self.recent_errors = []
        self.error_threshold = 5  # Alert after 5 errors
    
    def add_error(self, error):
        self.recent_errors.append(error)
        
        # Clean old errors (older than 1 hour)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        self.recent_errors = [e for e in self.recent_errors if e.timestamp > cutoff]
        
        # Check if we should alert
        if len(self.recent_errors) >= self.error_threshold:
            self.send_alert()
```

### 4. Terminal Collector Fix (Priority: Medium)

#### Problem
Terminal collector hasn't run in 75 hours

#### Investigation Needed
- [ ] Check if terminal collector has permission issues
- [ ] Verify terminal history file location
- [ ] Test manual execution

#### Terminal Collector Enhancement
```python
class TerminalCollector:
    def __init__(self):
        self.history_files = [
            Path.home() / ".bash_history",
            Path.home() / ".zsh_history",
            Path("/var/log/syslog"),  # System logs
        ]
    
    def run(self):
        """Collect terminal activity with fallbacks"""
        results = {
            "success": False,
            "data": {},
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }
        
        for history_file in self.history_files:
            if history_file.exists():
                try:
                    results["data"][history_file.name] = self.parse_history(history_file)
                    results["success"] = True
                except PermissionError:
                    log_warning(f"Permission denied for {history_file}")
                except Exception as e:
                    log_error(f"Error reading {history_file}: {e}")
        
        return results
```

### 5. UI Integration Improvements (Priority: Medium)

#### Current State
- Compass shows basic status
- No drill-down capability
- No historical trends

#### Enhancements
```javascript
// Add to Compass UI
const CompassEnhancements = {
    // Show last collection times
    showCollectorStatus: function() {
        return fetch('/api/compass/collectors')
            .then(r => r.json())
            .then(data => {
                this.displayCollectorGrid(data);
            });
    },
    
    // Show trends over time
    showTrends: function() {
        return fetch('/api/compass/trends')
            .then(r => r.json())
            .then(data => {
                this.renderTrendCharts(data);
            });
    },
    
    // Manual refresh button
    refreshCollectors: function() {
        return fetch('/api/compass/refresh', {method: 'POST'})
            .then(() => {
                this.showNotification('Collectors refreshed');
                setTimeout(() => location.reload(), 2000);
            });
    }
};
```

### 6. API Endpoints for Compass (Priority: Low)

#### New Endpoints to Add
```python
@app.route('/api/compass/status')
def compass_status():
    """Get real-time compass status"""
    director = CompassDirector()
    return jsonify(director.analyze())

@app.route('/api/compass/collectors')
def collector_status():
    """Get individual collector status"""
    return jsonify(get_collector_status())

@app.route('/api/compass/refresh', methods=['POST'])
def refresh_collectors():
    """Manually trigger collector run"""
    results = run_all_collectors()
    return jsonify({"success": True, "results": results})
```

---

## Implementation Plan

### Phase 1: Immediate Fixes (This Session)
1. ✅ Fix datetime deprecation warnings
2. [ ] Run git/file collectors manually to update data
3. [ ] Debug terminal collector issues
4. [ ] Add basic error logging

### Phase 2: Reliability (Next Session)
1. [ ] Implement retry logic for collectors
2. [ ] Add dynamic scheduling based on dev hours
3. [ ] Create collector health monitoring
4. [ ] Add error aggregation and alerting

### Phase 3: UI/UX Improvements (Future)
1. [ ] Add manual refresh button to Compass
2. [ ] Show collector last run times
3. [ ] Add trend visualization
4. [ ] Implement drill-down for issues

### Phase 4: Advanced Features (Future)
1. [ ] Predictive collector scheduling
2. [ ] Integration with Git hooks for immediate updates
3. [ ] Machine learning for anomaly detection
4. [ ] Automated issue resolution suggestions

---

## Testing Strategy

### Unit Tests
```python
def test_collector_retry():
    """Test retry logic for failed collectors"""
    collector = MockFailingCollector(fail_count=2)
    runner = CollectorRunner()
    result = runner.run_with_retry(collector)
    assert result["success"] == True

def test_dynamic_scheduling():
    """Test interval adjustment based on time"""
    interval = get_dynamic_interval("git")
    if is_active_development_hours():
        assert interval == timedelta(minutes=30)
    else:
        assert interval == timedelta(hours=4)
```

### Integration Tests
- Test full collector pipeline
- Test UI updates after collector runs
- Test error handling and recovery

### Monitoring
- Collector success rate
- Average collection time
- Error frequency and types
- UI responsiveness

---

## Success Metrics

### Reliability
- Collector uptime: >95%
- Data freshness: <30 minutes during active hours
- Error recovery: <5 minutes

### User Experience
- Compass reflects current state
- Clear indication of data freshness
- Actionable insights for issues
- One-click resolution for common problems

### System Health
- No silent failures
- Proactive issue detection
- Automated recovery where possible
- Clear error messages and suggested actions

---

## Rollout Plan

1. **Test in dev environment** - Validate all changes
2. **Gradual rollout** - Enable features one at a time
3. **Monitor closely** - Watch for regressions
4. **User feedback** - Collect and iterate
5. **Full deployment** - Enable all features

---

## Conclusion

The Compass system is a critical component for maintaining system awareness and proactive issue detection. These hardening improvements will make it more reliable, responsive, and valuable for daily development work.

The focus is on:
- **Reliability** - Collectors that always work
- **Freshness** - Data that reflects current state
- **Actionability** - Clear insights and resolutions
- **Visibility** - Understanding system health at a glance

By implementing these improvements, the Compass will transition from a passive monitoring tool to an active system health advisor.
