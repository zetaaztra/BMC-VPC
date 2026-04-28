
import sys
from unittest.mock import MagicMock

# Mock Streamlit
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

# Better column mock
def mock_columns(n):
    return [MagicMock() for _ in range(n)]
mock_st.columns.side_effect = mock_columns
mock_st.sidebar = MagicMock()
mock_st.sidebar.__enter__ = MagicMock(return_value=MagicMock())
mock_st.sidebar.__exit__ = MagicMock(return_value=None)

# Mock session state
class MockSessionState(dict):
    def __getattr__(self, key): return self.get(key)
    def __setattr__(self, key, val): self[key] = val

mock_ss = MockSessionState()
mock_st.session_state = mock_ss


# Import the app (we need to be careful with global st calls)
# To avoid execution of the whole script on import, I'll read the file and extract functions 
# or just mock everything.
# Actually, I'll just run a sub-script that defines the logic.

import canvas_studio_pro_v5 as app

def run_stress_test():
    print("🚀 Starting Stress Test...")
    
    # 1. Initialize
    app.init()
    print("✅ Initialization passed.")
    
    # 2. Test PDF with Empty Data
    try:
        pdf = app.to_pdf("Test_Empty", "A4", "Landscape")
        if pdf: print("✅ PDF (Empty Data) generated.")
    except Exception as e:
        print(f"❌ PDF (Empty) failed: {e}")
        return

    # 3. Test PDF with EXTREME Data
    extreme_text = "OVERFLOW TEST " * 1000 # ~14,000 characters
    for k in app.ALL:
        mock_ss.canvas[k] = extreme_text
    
    try:
        pdf = app.to_pdf("Test_Extreme", "A5", "Portrait")
        if pdf: print("✅ PDF (Extreme Data) generated without crash.")
    except Exception as e:
        print(f"❌ PDF (Extreme) failed: {e}")
        return

    # 4. Test PDF with Special Characters
    special_text = "🚀 Emoji Test | 中文测试 | !@#$%^&*()_+{}|:\"<>?"
    for k in app.ALL:
        mock_ss.canvas[k] = special_text
    
    try:
        pdf = app.to_pdf("Test_Special", "Letter", "Landscape")
        if pdf: print("✅ PDF (Special Chars) generated.")
    except Exception as e:
        print(f"❌ PDF (Special) failed: {e}")
        return

    # 5. Test JSON Export/Import
    try:
        json_data = app.to_json("test")
        # Simulate upload
        mock_up = MagicMock()
        mock_up.name = "test.json"
        mock_up.getvalue.return_value = json_data
        ok, msg = app.load_upload(mock_up)
        if ok: print("✅ JSON Export/Import cycle passed.")
        else: print(f"❌ JSON Load failed: {msg}")
    except Exception as e:
        print(f"❌ JSON Test failed: {e}")
        return

    print("\n🏆 STRESS TEST COMPLETE: ALL SYSTEMS NOMINAL.")

if __name__ == "__main__":
    run_stress_test()
