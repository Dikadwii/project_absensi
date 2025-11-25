#!/usr/bin/env python3
"""
Quick verification script to test if app is ready for Vercel deployment.
Run this before pushing to GitHub.
"""

import os
import sys

def check_files():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'database.py',
        'requirements.txt',
        'vercel.json',
        'templates/',
        'static/',
    ]
    
    print("📋 Checking required files...\n")
    all_good = True
    
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_good = False
    
    return all_good

def check_imports():
    """Check if all required modules can be imported."""
    print("\n📦 Checking Python imports...\n")
    
    required_imports = [
        'flask',
        'werkzeug',
        'sqlite3',
    ]
    
    all_good = True
    for module in required_imports:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_app_syntax():
    """Check if app.py has valid syntax."""
    print("\n🔍 Checking app.py syntax...\n")
    
    try:
        with open('app.py', 'r') as f:
            compile(f.read(), 'app.py', 'exec')
        print("  ✓ app.py syntax valid")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error in app.py: {e}")
        return False

def check_database_syntax():
    """Check if database.py has valid syntax."""
    print("\n🔍 Checking database.py syntax...\n")
    
    try:
        with open('database.py', 'r') as f:
            compile(f.read(), 'database.py', 'exec')
        print("  ✓ database.py syntax valid")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error in database.py: {e}")
        return False

def main():
    print("=" * 60)
    print("  🚀 VERCEL DEPLOYMENT READINESS CHECK")
    print("=" * 60 + "\n")
    
    checks = [
        ("Files", check_files()),
        ("Imports", check_imports()),
        ("app.py", check_app_syntax()),
        ("database.py", check_database_syntax()),
    ]
    
    print("\n" + "=" * 60)
    print("  📊 SUMMARY")
    print("=" * 60)
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    all_passed = all(result for _, result in checks)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ READY TO DEPLOY!")
        print("  ")
        print("  Next steps:")
        print("    1. git add .")
        print("    2. git commit -m 'Ready for Vercel deployment'")
        print("    3. git push origin main")
        print("    4. Deploy via https://vercel.com/dashboard")
        print("\n  See DEPLOY_GUIDE.md for detailed instructions.")
    else:
        print("  ❌ NOT READY - Fix errors above first!")
        sys.exit(1)
    
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
