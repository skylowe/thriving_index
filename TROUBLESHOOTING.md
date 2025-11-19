# Dashboard Troubleshooting Guide

## Step-by-Step Diagnosis

### Step 1: Verify Python Installation

Open Command Prompt or PowerShell and run:

```bash
python --version
```

**Expected output:** `Python 3.8.x` or higher

**If you see an error:**
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

---

### Step 2: Check Environment

Run this diagnostic script:

```bash
python check_environment.py
```

**Expected output:**
```
✓ streamlit: 1.28.x
✓ plotly: 5.17.x
✓ pandas: 1.5.x
✓ numpy: 1.24.x
```

**If you see "NOT INSTALLED":**
- Run the installation command shown in the output
- OR run: `pip install streamlit plotly pandas numpy`

---

### Step 3: Install Dependencies (if needed)

```bash
pip install streamlit plotly pandas numpy
```

**If that fails, try:**

```bash
python -m pip install streamlit plotly pandas numpy
```

**Wait for installation to complete** - this may take 2-3 minutes.

---

### Step 4: Test with Simple Dashboard

Run this minimal test:

```bash
streamlit run test_dashboard.py
```

**OR:**

```bash
python -m streamlit run test_dashboard.py
```

**Expected output in terminal:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Expected in browser:**
- A page saying "🎉 Streamlit is Working!"

**If the test dashboard works:**
- Your environment is fine
- The issue is with the main dashboard.py
- Proceed to Step 5

**If the test dashboard doesn't work:**
- Copy and paste the ENTIRE terminal output and send it to me
- Include any error messages

---

### Step 5: Check Data Files

Run this command:

```bash
dir data\results
```

**Expected output:**
- `thriving_index_overall.csv`
- `thriving_index_by_component.csv`
- `thriving_index_detailed_scores.csv`

**If files are missing:**
- Run: `python scripts/calculate_thriving_index.py`
- This will regenerate the results files

---

### Step 6: Run Full Dashboard

```bash
streamlit run dashboard.py
```

**OR:**

```bash
python -m streamlit run dashboard.py
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install streamlit
```

### Issue: "Port 8501 is already in use"

**Solution:** Use a different port:
```bash
streamlit run dashboard.py --server.port 8502
```

Then visit: http://localhost:8502

### Issue: "FileNotFoundError" for CSV files

**Solution:** Regenerate results:
```bash
python scripts/calculate_thriving_index.py
```

### Issue: Browser shows "This site can't be reached"

**Possible causes:**
1. Streamlit isn't actually running (check terminal for errors)
2. Firewall blocking localhost (try disabling temporarily)
3. Wrong URL (make sure it's http://localhost:8501 not https)

### Issue: Dashboard starts but shows errors

**Solution:** Check the terminal output for Python errors

---

## What to Send Me for Help

If none of this works, please send me:

1. **Output from:** `python check_environment.py`
2. **Output from:** `streamlit run test_dashboard.py` (the entire terminal output)
3. **Any error messages** you see in red
4. **Windows version:** Run `winver`
5. **Python version:** Already have from Step 1

---

## Quick Reference

**Install everything:**
```bash
pip install streamlit plotly pandas numpy
```

**Run dashboard:**
```bash
streamlit run dashboard.py
```

**Check files exist:**
```bash
dir data\results
```

**Regenerate results:**
```bash
python scripts/calculate_thriving_index.py
```
