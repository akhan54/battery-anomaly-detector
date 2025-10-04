"""
One-command execution of Battery_Anomaly_Detection.ipynb
Usage: python run.py (or python3 run.py)
"""
import sys
import os

# Fix for Windows asyncio/ZMQ compatibility
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import subprocess
from pathlib import Path

def main():
    # Check if notebook exists
    notebook_path = Path("Battery_Anomaly_Detection.ipynb")
    if not notebook_path.exists():
        print(f"❌ Error: {notebook_path} not found in current directory")
        return 1
    
    # Check if CSV exists (optional but helpful)
    csv_path = Path("Battery_Data_Cleaned.csv")
    if not csv_path.exists():
        print(f"⚠️  Warning: {csv_path} not found - notebook may fail if it requires this file")
    
    # Ensure outputs directory exists
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    print(f"✓ Outputs directory ready: {outputs_dir}")
    
    # Execute notebook using nbconvert
    try:
        import nbconvert
        from nbconvert.preprocessors import ExecutePreprocessor
        import nbformat
        
        print(f"\nExecuting {notebook_path}...")
        print("=" * 60)
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Execute with generous timeout (30 minutes)
        ep = ExecutePreprocessor(timeout=1800, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': '.'}})
        
        # Write executed notebook back (in-place execution)
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        print("=" * 60)
        print(f"✅ Successfully executed {notebook_path}")
        print(f"✓ Check outputs/ directory for results")
        print(f"✓ Check anomaly_summary.csv for summary data")
        print(f"✓ Check report.html for HTML report")
        return 0
        
    except ImportError as e:
        print(f"\n❌ Error: Missing required package")
        print(f"   {e}")
        print(f"\n💡 Install with: pip install jupyter nbconvert ipykernel")
        return 1
    except Exception as e:
        print(f"\n❌ Error executing notebook:")
        print(f"   {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())