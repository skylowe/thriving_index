"""
Check if the environment is set up correctly for the dashboard.
"""
import sys

print("=" * 60)
print("Environment Check for Thriving Index Dashboard")
print("=" * 60)

# Check Python version
print(f"\nPython version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Check required packages
packages = ['streamlit', 'plotly', 'pandas', 'numpy']
missing = []

for package in packages:
    try:
        mod = __import__(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {package}: {version}")
    except ImportError:
        print(f"✗ {package}: NOT INSTALLED")
        missing.append(package)

print("\n" + "=" * 60)

if missing:
    print(f"\n⚠️  Missing packages: {', '.join(missing)}")
    print("\nTo install missing packages, run:")
    print(f"  pip install {' '.join(missing)}")
else:
    print("\n✓ All required packages are installed!")
    print("\nYou can now run the dashboard with:")
    print("  streamlit run dashboard.py")

print("\n" + "=" * 60)
