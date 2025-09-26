"""Naver login service using Playwright with cookie reuse and persistence."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import httpx

from app.core.errors import LoginError
from app.infra.browser import BrowserClient

NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login?mode=form&url=https://new.smartplace.naver.com/"
NAVER_PROFILE_URL = "https://nid.naver.com/user2/help/myInfoV2?lang=ko_KR"
SMARTPLACE_HOME_URL = "https://new.smartplace.naver.com/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass
class LoginResult:
    success: bool
    used_cookies: bool
    message: str
    csrf_token: str | None = None


class NaverLoginService:
    def __init__(
        self,
        storage_path: Path | str = ".auth/cookies.json",
        headless: bool = False,
        browser_type: str | None = None,
    ) -> None:
        self.storage_path = Path(storage_path)
        self.headless = headless
        self.browser_type = browser_type
        self._csrf_token_path = self.storage_path.parent / "csrf_token.txt"
        self._csrf_token: str | None = None

    def get_authenticated_client(self) -> httpx.Client:
        """Create and return an authenticated httpx client using stored session data."""
        if not self.storage_path.exists():
            raise LoginError(
                "쿠키 파일이 없습니다. 먼저 로그인을 성공적으로 수행해야 합니다."
            )

        try:
            with self.storage_path.open("r", encoding="utf-8") as f:
                cookie_data = json.load(f)
            cookies = cookie_data.get("cookies", [])
        except (OSError, json.JSONDecodeError) as e:
            raise LoginError(f"쿠키 파일을 읽거나 파싱하는 데 실패했습니다: {e}") from e

        client = httpx.Client()
        for cookie in cookies:
            client.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"])

        # Set a universal user agent
        client.headers["User-Agent"] = USER_AGENT

        return client


    def login(
        self, user_id: str, password: str, force_credential_login: bool = False
    ) -> LoginResult:
        client = BrowserClient()
        client.initialize(
            headless=self.headless, slow_mo_ms=100, browser_type=self.browser_type
        )
        try:
            # 1) Try cookie-based session first if available and not forcing credential login
            if not force_credential_login and self.storage_path.exists():
                context = client.new_context(self.storage_path)
                page = context.new_page()

                # Navigate to profile page to validate cookies (same as original)
                page.goto(NAVER_PROFILE_URL, wait_until="load")
                sleep(3.0)  # Wait for potential redirection like original

                # Check if redirected to login page - if not, cookies are valid
                if "login" not in page.url:
                    # Cookies are valid, ensure SmartPlace session and persist state
                    self._ensure_smartplace_session(page)
                    client.save_storage_state(context, self.storage_path)
                    context.close()
                    return LoginResult(
                        True, True, "저장된 쿠키로 로그인되었습니다.", self._csrf_token
                    )

                # Cookies are invalid, close context and proceed to credential login
                context.close()

            # 2) Perform credential login exactly like original
            context = client.new_context()
            page = context.new_page()

            # Use exact URL from original code
            page.goto(
                "https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/",
                wait_until="load",
            )

            # Use JavaScript to set values exactly like original
            # Use JavaScript to set the input values directly (fix unterminated string and syntax)
            page.evaluate(
                f'document.querySelector("input[id=\'id\']").setAttribute("value", "{user_id}");'
            )
            page.evaluate(
                f'document.querySelector("input[id=\'pw\']").setAttribute("value", "{password}");'
            )

            # Click login button using exact selector from original
            page.click("#log\\.login")
            sleep(1.0)

            # Wait for redirect to naver.com like original
            try:
                page.wait_for_url(re.compile(r".*naver\.com.*"), timeout=10000)
                sleep(1.0)  # Additional wait for stability

                # Ensure SmartPlace session is established
                self._ensure_smartplace_session(page)

                # Save cookies to storage
                client.save_storage_state(context, self.storage_path)
                context.close()
                return LoginResult(
                    True, False, "아이디/비밀번호로 로그인 성공", self._csrf_token
                )

            except Exception:
                current_url = page.url
                raise LoginError(
                    f"로그인 실패: 예상 도메인으로 리다이렉트되지 않음 (현재 URL: {current_url})"
                )

        except LoginError as e:
            return LoginResult(False, False, str(e))
        except Exception as e:  # noqa: BLE001 - surface to UI
            return LoginResult(False, False, f"알 수 없는 오류: {e}")
        finally:
            client.close()



    def _ensure_smartplace_session(self, page) -> None:
        """Ensure SmartPlace domain cookies (e.g., csrf_token) are populated."""
        page.goto(SMARTPLACE_HOME_URL, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        sleep(2.0)  # Wait for session to be established

        # Extract CSRF token from page
        try:
            csrf_token = None

            try:
                state_summary = page.evaluate(
                    """
                    () => {
                        const state = window.__SMARTPLACE_INIT_STATE__ || window.__APOLLO_STATE__ || null;
                        if (!state) return null;
                        const json = JSON.stringify(state);
                        return json.slice(0, 2000);
                    }
                    """
                )
                if state_summary:
                    print("[DEBUG] SMARTPLACE state snapshot available")
            except Exception as snapshot_exc:
                print(f"[DEBUG] Failed to capture SmartPlace state snapshot: {snapshot_exc}")

            # Method 1: Check for meta tag
            csrf_meta = page.query_selector('meta[name="csrf-token"]')
            if csrf_meta:
                csrf_token = (csrf_meta.get_attribute("content") or "").strip()
                if csrf_token:
                    print("[DEBUG] CSRF token from meta tag")

            if not csrf_token:
                csrf_token = page.evaluate(
                    """
                    () => {
                        const sources = [window.__SMARTPLACE_INIT_STATE__, window.__APOLLO_STATE__, window.__NUXT__];
                        const visited = new WeakSet();
                        const normalize = (value, depth = 0) => {
                            if (!value || depth > 8) return null;
                            if (typeof value === "string") {
                                const trimmed = value.trim();
                                if (!trimmed) return null;
                                if (trimmed.length > 8 && trimmed.toLowerCase().includes("csrf")) return trimmed;
                                return null;
                            }
                            if (typeof value === "number" || typeof value === "boolean") {
                                return String(value);
                            }
                            if (typeof value === "object") {
                                if (visited.has(value)) return null;
                                visited.add(value);
                                if (typeof value.csrfToken === "string") return value.csrfToken;
                                if (typeof value.token === "string" && value.token.toLowerCase().includes("csrf")) return value.token;
                                for (const [key, nested] of Object.entries(value)) {
                                    if (!key) continue;
                                    if (key.toLowerCase().includes("csrf")) {
                                        const extracted = normalize(nested, depth + 1);
                                        if (extracted) return extracted;
                                    }
                                    const extracted = normalize(nested, depth + 1);
                                    if (extracted) return extracted;
                                }
                            }
                            return null;
                        };

                        for (const source of sources) {
                            const extracted = normalize(source);
                            if (extracted) return extracted;
                        }
                        return null;
                    }
                    """
                )
                if csrf_token:
                    print("[DEBUG] CSRF token from bootstrapped state")

            # Method 2: Check for JavaScript variables
            if not csrf_token:
                csrf_token = page.evaluate("""() => {
                    // Look for common CSRF token patterns in window object
                    if (window.csrfToken) return window.csrfToken;
                    if (window._csrf) return window._csrf;
                    if (window.__CSRF_TOKEN__) return window.__CSRF_TOKEN__;

                    // Look in script tags
                    const scripts = document.querySelectorAll('script');
                    for (const script of scripts) {
                        const text = script.textContent;
                        if (!text) continue;

                        // Common patterns for CSRF token
                        const patterns = [
                            /csrfToken["']?\s*:\s*["']([^"']+)["']/,
                            /_token["']?\s*:\s*["']([^"']+)["']/,
                            /csrf["']?\s*:\s*["']([^"']+)["']/,
                        ];

                        for (const pattern of patterns) {
                            const match = text.match(pattern);
                            if (match) return match[1];
                        }
                    }
                    return null;
                }""")
                if csrf_token:
                    print("[DEBUG] CSRF token from script inspection")

            # Method 3: Inspect browser storage and known globals
            if not csrf_token:
                csrf_token = page.evaluate(
                    """
                    () => {
                        const visited = new WeakSet();
                        const normalize = (value, depth = 0) => {
                            if (!value || depth > 6) return null;
                            if (typeof value === "string") {
                                const trimmed = value.trim();
                                if (!trimmed || trimmed === "null" || trimmed === "undefined") {
                                    return null;
                                }
                                return trimmed;
                            }
                            if (typeof value === "number" || typeof value === "boolean") {
                                return String(value);
                            }
                            if (typeof value === "object") {
                                if (visited.has(value)) return null;
                                visited.add(value);
                                if (typeof value.csrfToken === "string") {
                                    const extracted = normalize(value.csrfToken, depth + 1);
                                    if (extracted) return extracted;
                                }
                                if (typeof value.token === "string") {
                                    const extracted = normalize(value.token, depth + 1);
                                    if (extracted) return extracted;
                                }
                                for (const [key, nested] of Object.entries(value)) {
                                    if (key && key.toLowerCase().includes("csrf")) {
                                        const extracted = normalize(nested, depth + 1);
                                        if (extracted) return extracted;
                                    }
                                }
                            }
                            return null;
                        };

                        const storages = [window.localStorage, window.sessionStorage];
                        for (const storage of storages) {
                            if (!storage) continue;
                            for (let i = 0; i < storage.length; i += 1) {
                                const key = storage.key(i);
                                try {
                                    const raw = storage.getItem(key);
                                    if (!raw) continue;
                                    let extracted = normalize(raw);
                                    if (extracted) return extracted;
                                    try {
                                        const parsed = JSON.parse(raw);
                                        extracted = normalize(parsed);
                                        if (extracted) return extracted;
                                    } catch {
                                        // ignore JSON parse error
                                    }
                                } catch {
                                    continue;
                                }
                            }
                        }

                        const globals = [
                            window.__APOLLO_STATE__,
                            window.__SMARTPLACE_INIT_STATE__,
                            window.__SMARTPLACE_STORE__,
                            window.__NUXT__,
                        ];
                        for (const state of globals) {
                            const extracted = normalize(state);
                            if (extracted) return extracted;
                        }

                        if (typeof window.getCsrfToken === "function") {
                            try {
                                const maybe = window.getCsrfToken();
                                const extracted = normalize(maybe);
                                if (extracted) return extracted;
                            } catch {
                                // ignore errors from custom getters
                            }
                        }

                        return null;
                    }
                    """
                )

            # Method 4: Check non-httpOnly cookies via document.cookie
            if not csrf_token:
                csrf_token = page.evaluate(
                    """
                    () => {
                        const parts = document.cookie.split(";");
                        for (const part of parts) {
                            const trimmed = part.trim();
                            if (!trimmed) continue;
                            if (!trimmed.toLowerCase().includes("csrf")) continue;
                            const index = trimmed.indexOf("=");
                            if (index === -1) continue;
                            const value = trimmed.slice(index + 1).trim();
                            if (value && value !== "null" && value !== "undefined") {
                                return value;
                            }
                        }
                        return null;
                    }
                    """
                )

            # Method 5: Check cookies for csrf token
            if not csrf_token:
                cookies = page.context.cookies()
                for cookie in cookies:
                    name = cookie.get("name", "")
                    value = cookie.get("value")
                    if name and "csrf" in name.lower() and value:
                        csrf_token = value
                        break

            if csrf_token:
                csrf_token = (csrf_token or "").strip()

            if csrf_token:
                print(f"[DEBUG] CSRF token found: {csrf_token[:10]}...")
                # Store the token for later use (could be stored in a class variable)
                self._csrf_token = csrf_token
                # Add the token to the browser context so it's saved with other cookies
                page.context.add_cookies([
                    {
                        "name": "csrf_token",
                        "value": csrf_token,
                        "domain": ".naver.com",
                        "path": "/",
                    }
                ])
                print("[DEBUG] CSRF token injected into browser context for persistence.")
            else:
                print("[WARNING] CSRF token not found on SmartPlace page")
                self._csrf_token = None

        except Exception as e:
            print(f"[DEBUG] Error extracting CSRF token: {e}")
            self._csrf_token = None
        finally:
            if not self._csrf_token:
                self._warm_up_smartplace_csrf(page)

    def _warm_up_smartplace_csrf(self, page) -> None:
        """Attempt to trigger SmartPlace to issue a CSRF token via background fetch."""
        try:
            warmup_result = page.evaluate(
                """
                () => {
                    const payload = { operationName: "WarmupCSRF", query: "query WarmupCSRF { __typename }", variables: {} };
                    return fetch("https://new.smartplace.naver.com/graphql?opName=WarmupCSRF", {
                        method: "POST",
                        headers: {
                            "content-type": "application/json",
                            "accept": "*/*",
                            "x-requested-with": "XMLHttpRequest",
                        },
                        credentials: "include",
                        body: JSON.stringify(payload),
                        mode: "cors",
                    }).then(res => {
                        return res.text().then(text => ({ ok: res.ok, text }));
                    }).catch(err => ({ ok: false, text: String(err) }));
                }
                """,
                timeout=5000,
            )
            if isinstance(warmup_result, dict):
                text = warmup_result.get("text") or ""
                snippet = text[:200]
                print(f"[DEBUG] Warm-up request status: {warmup_result.get('ok')} body snippet: {snippet}")
                if text:
                    try:
                        payload = json.loads(text)
                        token_from_body = None
                        if isinstance(payload, dict):
                            token_from_body = payload.get("csrfToken") or payload.get("token")
                            if not token_from_body:
                                for value in payload.values():
                                    if isinstance(value, dict):
                                        if value.get("csrfToken"):
                                            token_from_body = value["csrfToken"]
                                            break
                        if token_from_body and isinstance(token_from_body, str):
                            token_from_body = token_from_body.strip()
                            if token_from_body and "csrf" in token_from_body.lower():
                                self._csrf_token = token_from_body
                                print("[DEBUG] CSRF token extracted from warm-up body")
                    except Exception as parse_exc:  # noqa: BLE001 - diagnostic only
                        print(f"[DEBUG] Warm-up response parse failed: {parse_exc}")
            sleep(1.0)
            cookies = page.context.cookies()
            for cookie in cookies:
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                if name and "csrf" in name.lower() and value:
                    self._csrf_token = value
                    print("[DEBUG] CSRF token obtained from warm-up request")
                    break
        except Exception as exc:
            print(f"[DEBUG] CSRF warm-up failed: {exc}")
        finally:
            if not self._csrf_token:
                print("[WARNING] CSRF token still missing after warm-up attempt")
