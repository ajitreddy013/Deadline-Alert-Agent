from __future__ import annotations

from pathlib import Path
import os
import time
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


PROFILE_SUBDIR = "whatsapp_profile"
PROFILE_BASE = Path(os.path.expanduser("~/.deadline_reminder"))
PROFILE_DIR = PROFILE_BASE / PROFILE_SUBDIR


def _ensure_profile_dir() -> str:
    PROFILE_BASE.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return str(PROFILE_DIR)


def _find_element_any(driver, by_and_value_list, timeout: int = 10):
    last_exc = None
    for by, value in by_and_value_list:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception as e:
            last_exc = e
            continue
    if last_exc:
        raise last_exc
    return None


def _find_elements_any(driver, by_and_value_list):
    for by, value in by_and_value_list:
        els = driver.find_elements(by, value)
        if els:
            return els
    return []


def _log_chrome_version_info(driver) -> None:
    """Log Chrome and ChromeDriver versions and warn if major versions mismatch."""
    try:
        caps = getattr(driver, "capabilities", {}) or {}
        browser_version = caps.get("browserVersion") or caps.get("version")
        chrome_info = caps.get("chrome", {}) or {}
        chromedriver_version_raw = chrome_info.get("chromedriverVersion", "")
        chromedriver_version = chromedriver_version_raw.split(" ")[0] if chromedriver_version_raw else None
        if browser_version:
            print(f"Chrome browser version: {browser_version}")
        if chromedriver_version:
            print(f"ChromeDriver version: {chromedriver_version}")
        # Compare major versions
        if browser_version and chromedriver_version:
            browser_major = browser_version.split(".")[0]
            driver_major = chromedriver_version.split(".")[0]
            if browser_major != driver_major:
                print("⚠️ Chrome and ChromeDriver major versions may not match. Consider updating Chrome or the driver.")
    except Exception:
        # Non-fatal if we cannot determine versions
        pass


def _get_search_box(driver) -> Optional[object]:
    candidates = [
        (By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]'),  # legacy
        (By.XPATH, '//div[@role="textbox" and @contenteditable="true"]'),
        (By.CSS_SELECTOR, 'div[contenteditable="true"][role="textbox"]'),
    ]
    try:
        return _find_element_any(driver, candidates, timeout=10)
    except Exception:
        return None


def _find_chat(driver, chat_name: str):
    candidates = [
        (By.XPATH, f'//span[@title="{chat_name}"]'),  # legacy title
        (By.XPATH, f'//div[@role="gridcell"]//span[@title="{chat_name}"]'),
        (By.XPATH, f'//span[@dir="auto" and @title="{chat_name}"]'),
        (By.XPATH, f'//span[@dir="auto" and normalize-space(text())="{chat_name}"]'),
    ]
    return _find_element_any(driver, candidates, timeout=15)


def fetch_whatsapp_messages(chat_name: str, num_messages: int = 10, wait_timeout: int = 120) -> List[Dict]:
    """
    Launch WhatsApp Web, ensure session (QR on first run), open chat by name, and
    return the last N textual messages.

    Session is persisted under ~/.deadline_reminder/whatsapp_profile so you don't
    have to re-scan the QR each time.
    """
    options = Options()
    options.add_argument(f"--user-data-dir={_ensure_profile_dir()}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Do NOT run headless for QR login

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    _log_chrome_version_info(driver)
    driver.set_window_size(1280, 900)

    try:
        driver.get("https://web.whatsapp.com/")
        print("If prompted, scan the QR code with WhatsApp on your phone.")

        # Wait until either the search box appears (logged-in state) or timeout
        try:
            WebDriverWait(driver, wait_timeout).until(
                lambda d: _get_search_box(d) is not None
            )
        except TimeoutException:
            raise TimeoutException(
                "Timed out waiting for WhatsApp Web login. Please scan the QR and try again."
            )

        # Find search box and locate the chat
        search_box = _get_search_box(driver)
        if not search_box:
            raise RuntimeError("Could not locate WhatsApp search box. UI may have changed.")

        search_box.click()
        # Clear existing text (send Ctrl/Command+A then Backspace)
        try:
            # Mac uses COMMAND
            from selenium.webdriver.common.keys import Keys
            search_box.send_keys(Keys.COMMAND, "a")
            search_box.send_keys(Keys.BACKSPACE)
        except Exception:
            pass
        search_box.send_keys(chat_name)

        # Wait for chat result then click it
        chat_el = _find_chat(driver, chat_name)
        if not chat_el:
            raise NoSuchElementException(f"Chat named '{chat_name}' not found.")
        chat_el.click()

        # Let messages render
        time.sleep(2)

        # Try multiple selectors for message containers
        msg_containers = _find_elements_any(driver, [
            (By.XPATH, '//div[contains(@data-testid, "msg-container")]'),            # newer
            (By.CSS_SELECTOR, 'div.message-in, div.message-out'),                    # legacy
            (By.XPATH, '//div[contains(@class, "message-")]'),                      # fallback
        ])

        results: List[Dict] = []
        for msg in msg_containers[-num_messages:]:
            text = ""
            # Try several ways to get message text
            try:
                text = msg.find_element(By.CSS_SELECTOR, 'span.selectable-text.copyable-text').text
            except Exception:
                try:
                    text = msg.find_element(By.CSS_SELECTOR, 'span[dir="auto"]').text
                except Exception:
                    try:
                        text = msg.text or ""
                    except Exception:
                        text = ""
            text = (text or "").strip()
            if text:
                results.append({"text": text})

        return results

    finally:
        try:
            driver.quit()
        except Exception:
            pass
