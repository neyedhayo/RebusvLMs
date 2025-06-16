import os
import sys
import subprocess
from pathlib import Path

def get_latest_experiment():
    """Get the most recent experiment timestamp"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return None
    
    # Get all timestamp directories
    timestamps = [d.name for d in logs_dir.iterdir() if d.is_dir() and d.name.replace('_', '').isdigit()]
    
    if not timestamps:
        return None
    
    # Sort by timestamp (newest first)
    timestamps.sort(reverse=True)
    return timestamps[0]

def run_evaluation(timestamp: str, include_f1: bool = True, debug: bool = False):
    """Run evaluation with the given timestamp"""
    cmd = [sys.executable, "-m", "experiments.evaluate", "--timestamp", timestamp]
    
    if include_f1:
        cmd.append("--use-f1")
    
    if debug:
        cmd.append("--debug")
    
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0

def main():
    print("🔍 Quick Evaluation Tool")
    print("=" * 30)
    
    # Check if a specific timestamp was provided
    if len(sys.argv) > 1:
        timestamp = sys.argv[1]
        print(f"📅 Using provided timestamp: {timestamp}")
    else:
        # Get the latest experiment
        timestamp = get_latest_experiment()
        if not timestamp:
            print("❌ No experiments found in logs/ directory")
            print("💡 Run an experiment first:")
            print("   python -m experiments.run_experiment --config gemini1.5.yaml --prompt-style zero_shot")
            sys.exit(1)
        
        print(f"📅 Using latest experiment: {timestamp}")
    
    # Check if results exist
    results_file = Path(f"logs/{timestamp}/results.json")
    if not results_file.exists():
        print(f"❌ No results.json found for {timestamp}")
        sys.exit(1)
    
    print(f"📁 Found results: {results_file}")
    
    # Ask user what to run
    print(f"\n🔧 What would you like to do?")
    print(f"1. Debug analysis only")
    print(f"2. Quick evaluation (exact match + F1)")
    print(f"3. Detailed evaluation with debug output")
    print(f"4. All of the above")
    
    choice = input("\nEnter choice (1-4) or press Enter for option 2: ").strip()
    
    if choice == "1":
        print(f"\n🔍 Running debug analysis...")
        subprocess.run([sys.executable, "debug_results.py", timestamp])
    
    elif choice == "3":
        print(f"\n📊 Running detailed evaluation...")
        run_evaluation(timestamp, include_f1=True, debug=True)
    
    elif choice == "4":
        print(f"\n🔍 Running debug analysis...")
        subprocess.run([sys.executable, "debug_results.py", timestamp])
        print(f"\n📊 Running detailed evaluation...")
        run_evaluation(timestamp, include_f1=True, debug=True)
    
    else:  # Default: choice == "2" or Enter
        print(f"\n📊 Running quick evaluation...")
        run_evaluation(timestamp, include_f1=True, debug=False)
    
    print(f"\n✅ Evaluation complete!")
    print(f"📁 Check metrics at: logs/{timestamp}/metrics.json")

if __name__ == "__main__":
    main()