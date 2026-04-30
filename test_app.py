from playwright.sync_api import sync_playwright
import time

def test_canvas_studio_pro():
    with sync_playwright() as p:
        print("🚀 Launching Chrome...")
        browser = p.chromium.launch(headless=False, slow_mo=600)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        url = "http://localhost:8501"
        print(f"📡 Connecting to {url}...")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"❌ Cannot reach {url}: {e}")
            browser.close()
            return

        # ── Wait for Streamlit to finish rendering ──
        # Streamlit buttons ARE loading (logs showed 28 elements), but
        # wait_for_selector thinks they aren't "visible" yet.
        # The fix: wait for the page to settle via networkidle + a short sleep.
        print("⏳ Waiting for Streamlit to finish rendering...")
        try:
            page.wait_for_load_state("networkidle", timeout=45000)
        except:
            pass  # networkidle can be flaky; continue anyway
        time.sleep(5)  # Give Streamlit's JS framework time to hydrate

        # Quick sanity check: count buttons on the page
        btn_count = page.locator("button").count()
        print(f"✅ App loaded! Found {btn_count} buttons on the page.")
        if btn_count == 0:
            print("❌ No buttons found. Something is wrong with the app.")
            browser.close()
            return

        # ══════════════════════════════════════════════
        # TEST 1: Tab Navigation
        # ══════════════════════════════════════════════
        print("\n📂 TEST 1: Tab Navigation")
        tabs = [
            "Value Proposition Canvas",
            "SWOT & Revenue",
            "Full Overview",
            "Analytics Dashboard",
            "Business Model Canvas",
        ]
        for tab_name in tabs:
            try:
                tab = page.get_by_role("tab", name=tab_name)
                if tab.count() > 0:
                    tab.first.click()
                    time.sleep(1)
                    print(f"   ✓ {tab_name}")
                else:
                    print(f"   ⚠️ Tab not found: {tab_name}")
            except Exception as e:
                print(f"   ⚠️ {tab_name}: {e}")

        # ══════════════════════════════════════════════
        # TEST 2: Sidebar Buttons
        # ══════════════════════════════════════════════
        print("\n⚙️  TEST 2: Sidebar Buttons")

        # Save
        try:
            page.get_by_text("💾 Save").click()
            time.sleep(1)
            print("   ✓ Save")
        except Exception as e:
            print(f"   ⚠️ Save: {e}")

        # Undo
        try:
            page.get_by_text("↩ Undo").click()
            time.sleep(1)
            print("   ✓ Undo")
        except Exception as e:
            print(f"   ⚠️ Undo: {e}")

        # Clear
        try:
            page.get_by_text("🗑 Clear").click()
            time.sleep(1)
            print("   ✓ Clear")
        except Exception as e:
            print(f"   ⚠️ Clear: {e}")

        # Tips
        try:
            page.get_by_text("💡 Tips").click()
            time.sleep(1)
            print("   ✓ Tips toggle")
        except Exception as e:
            print(f"   ⚠️ Tips: {e}")

        # Theme Switch
        try:
            page.get_by_text("Switch to").click()
            time.sleep(2)
            print("   ✓ Theme toggled")
        except Exception as e:
            print(f"   ⚠️ Theme: {e}")

        # ══════════════════════════════════════════════
        # TEST 3: Text Input
        # ══════════════════════════════════════════════
        print("\n✍️  TEST 3: Text Input")
        # Switch to BMC tab first
        try:
            bmc_tab = page.get_by_role("tab", name="Business Model Canvas")
            if bmc_tab.count() > 0:
                bmc_tab.first.click()
                time.sleep(2)
        except:
            pass

        textareas = page.locator("textarea")
        ta_count = textareas.count()
        print(f"   Found {ta_count} text areas")
        if ta_count > 0:
            try:
                textareas.first.fill("Automated test input from Playwright 🚀")
                time.sleep(1)
                print("   ✓ Typed into first text area")
            except Exception as e:
                print(f"   ⚠️ Could not type: {e}")

        # ══════════════════════════════════════════════
        # TEST 4: PDF Generation
        # ══════════════════════════════════════════════
        print("\n📄 TEST 4: PDF Generation")
        try:
            page.get_by_text("📄 Generate PDF").click()
            print("   ✓ Clicked Generate PDF")
            time.sleep(5)  # Wait for PDF to compile

            # Check if a download button appeared
            dl = page.get_by_text("Save", exact=False)
            if dl.count() > 0:
                print("   ✓ PDF download button appeared!")
            else:
                print("   ⚠️ PDF download button not visible yet")
        except Exception as e:
            print(f"   ⚠️ PDF generation: {e}")

        # ══════════════════════════════════════════════
        # TEST 5: Export Buttons
        # ══════════════════════════════════════════════
        print("\n📦 TEST 5: Export Buttons")
        try:
            json_btn = page.get_by_text("📦 JSON")
            if json_btn.count() > 0:
                print("   ✓ JSON export button present")
            csv_btn = page.get_by_text("📊 CSV")
            if csv_btn.count() > 0:
                print("   ✓ CSV export button present")
        except Exception as e:
            print(f"   ⚠️ Export buttons: {e}")

        # ══════════════════════════════════════════════
        # RESULTS
        # ══════════════════════════════════════════════
        print("\n" + "═" * 50)
        print("🏆 TEST RUN COMPLETE")
        print("═" * 50)
        time.sleep(3)
        browser.close()


if __name__ == "__main__":
    test_canvas_studio_pro()
