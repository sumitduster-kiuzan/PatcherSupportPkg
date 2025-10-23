#!/usr/bin/env python3
"""
Explanation and fix for the AttributeError: 'str' object has no attribute 'decode'

This error occurs when code tries to call .decode() on a string object that's already
decoded (i.e., it's already a str, not bytes).

In Python 3:
- bytes objects have a .decode() method to convert to str
- str objects do NOT have a .decode() method
- subprocess can return either bytes or str depending on configuration

The error happens in subprocess_wrapper.py line 177 in the generate_log method
when it tries to call .decode() on what's already a string.
"""

def demonstrate_error():
    """Demonstrate the error that's occurring"""
    # This would cause the error:
    try:
        text = "Hello World"  # This is already a string
        decoded = text.decode("utf-8")  # ERROR: str has no decode method
    except AttributeError as e:
        print(f"Error: {e}")
        print("This is the same error you're seeing!")

def demonstrate_fix():
    """Demonstrate the proper fix"""
    def safe_decode(data):
        """Safely decode data whether it's bytes or str"""
        if isinstance(data, bytes):
            return data.decode("utf-8", errors="ignore")
        else:
            return str(data)
    
    # Test with bytes
    bytes_data = b"Hello World"
    print(f"Bytes input: {safe_decode(bytes_data)}")
    
    # Test with string
    str_data = "Hello World"
    print(f"String input: {safe_decode(str_data)}")
    
    # Test with None
    none_data = None
    print(f"None input: {safe_decode(none_data)}")

def fixed_generate_log_snippet():
    """
    This is how the generate_log method should be fixed in subprocess_wrapper.py
    """
    def generate_log(self, result, output=""):
        """
        Generate log output from subprocess result
        """
        if isinstance(result, subprocess.CompletedProcess):
            if result.stdout:
                if isinstance(result.stdout, bytes):
                    output += result.stdout.decode("utf-8", errors="ignore")
                else:
                    output += str(result.stdout)
            if result.stderr:
                if isinstance(result.stderr, bytes):
                    output += result.stderr.decode("utf-8", errors="ignore")
                else:
                    output += str(result.stderr)
        else:
            if isinstance(result, bytes):
                output += result.decode("utf-8", errors="ignore")
            else:
                output += str(result)
        
        return output

if __name__ == "__main__":
    print("=== Demonstrating the decode error ===")
    demonstrate_error()
    
    print("\n=== Demonstrating the fix ===")
    demonstrate_fix()
    
    print("\n=== Fix Summary ===")
    print("To fix this error in your OpenCore Legacy Patcher:")
    print("1. Open opencore_legacy_patcher/support/subprocess_wrapper.py")
    print("2. Find the generate_log method around line 177")
    print("3. Replace direct .decode() calls with isinstance() checks")
    print("4. Only call .decode() on bytes objects, use str() for strings")
    print("\nSee the patch file: fix_decode_error.patch")