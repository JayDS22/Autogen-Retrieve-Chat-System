"""
Script to run all example demonstrations
Author: Jay Guwalani
Usage: python scripts/run_examples.py
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

def run_example(example_name, script_path):
    """Run a single example script"""
    print(f"\n{'='*80}")
    print(f"Running: {example_name}")
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=300)
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {example_name} completed successfully in {execution_time:.2f}s")
            print("Output:")
            print(result.stdout)
        else:
            print(f"❌ {example_name} failed")
            print("Error:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ {example_name} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"💥 {example_name} crashed: {e}")
        return False

def main():
    """Run all examples"""
    print("AutoGen RetrieveChat - Running All Examples")
    print("Author: Jay Guwalani")
    
    examples_dir = project_root / "examples"
    examples = [
        ("Basic Q&A", examples_dir / "basic_qa.py"),
        ("Code Generation", examples_dir / "code_generation.py"),
        ("Multi-hop Reasoning", examples_dir / "multihop_reasoning.py"),
        ("Custom Prompts", examples_dir / "custom_prompts.py")
    ]
    
    results = []
    total_start_time = time.time()
    
    for example_name, script_path in examples:
        if script_path.exists():
            success = run_example(example_name, script_path)
            results.append((example_name, success))
        else:
            print(f"⚠️ Script not found: {script_path}")
            results.append((example_name, False))
        
        time.sleep(2)  # Brief pause between examples
    
    total_time = time.time() - total_start_time
    
    # Summary
    print(f"\n{'='*80}")
    print("EXAMPLE EXECUTION SUMMARY")
    print(f"{'='*80}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total Examples: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {successful/total*100:.1f}%")
    print(f"Total Execution Time: {total_time:.2f}s")
    
    print(f"\nDetailed Results:")
    for example_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {example_name}: {status}")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
