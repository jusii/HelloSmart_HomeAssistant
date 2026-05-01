"""Region-aware authentication and HMAC-SHA1 request signing for Smart API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
import uuid
from urllib.parse import urlparse, parse_qs, urlencode, quote

import aiohttp

from .const import (
    ACCEPT_HEADER,
    API_SESSION_PATH,
    EMPTY_BODY_MD5,
    EU_API_BASE_URL,
    EU_APP_ID,
    EU_AUTH_BASE_URL,
    EU_CONTEXT_URL,
    EU_DEVICE_ID_LENGTH,
    EU_GIGYA_SOCIALIZE_BASE,
    EU_IDENTITY_TYPE,
    EU_OPERATOR_CODE,
    EU_SIGNING_SECRET,
    EU_WEBVIEW_USER_AGENT,
    GIGYA_API_KEY,
    INTL_APP_ID,
    INTL_AUTH_BASE_URL,
    INTL_DEVICE_ID_LENGTH,
    INTL_IDENTITY_TYPE,
    INTL_OPERATOR_CODE,
    INTL_SIGNING_SECRET,
    INTL_VC_APP_SECRET,
    INTL_VEHICLE_APP_ID,
    INTL_X_CA_KEY,
    INTL_API_BASE_URL,
)
from .models import Account, AuthState, Region

_LOGGER = logging.getLogger(__name__)

# Token-like keys to scrub from bodies/URLs before they hit the log.
_REDACT_KEYS = (
    "access_token",
    "accessToken",
    "id_token",
    "idToken",
    "refresh_token",
    "refreshToken",
    "login_token",
    "code",
    "authCode",
    "password",
)
_REDACT_JSON_RE = re.compile(
    r'("(?:' + "|".join(_REDACT_KEYS) + r')"\s*:\s*")[^"]*(")'
)
_REDACT_QUERY_RE = re.compile(
    r"((?:" + "|".join(_REDACT_KEYS) + r")=)[^&\s\"<>]+"
)


def _redact(text: str, *, limit: int = 2048) -> str:
    """Best-effort scrub of token-like values from a response body or URL."""
    if not text:
        return text
    out = _REDACT_JSON_RE.sub(r"\1***\2", text)
    out = _REDACT_QUERY_RE.sub(r"\1***", out)
    if len(out) > limit:
        out = out[:limit] + f"...<+{len(out) - limit}b>"
    return out


def _generate_device_id(length: int) -> str:
    """Generate a random hex device identifier."""
    return secrets.token_hex(length // 2)


def _md5_base64(data: str | bytes) -> str:
    """Compute base64-encoded MD5 hash of data."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(hashlib.md5(data).digest()).decode()


def _create_sign(
    nonce: str,
    params: dict,
    timestamp: str,
    method: str,
    url: str,
    body: str | None = None,
    use_intl: bool = False,
    url_encode_params: bool = False,
) -> str:
    """Create HMAC-SHA1 signature matching reference pySmartHashtag utils."""
    body_md5 = _md5_base64(body) if body else EMPTY_BODY_MD5

    if url_encode_params and params:
        encoded_params = {k: quote(str(v), safe="") for k, v in params.items()}
        url_params = "&".join(f"{k}={v}" for k, v in encoded_params.items())
    elif params:
        url_params = "&".join(f"{k}={v}" for k, v in params.items())
    else:
        url_params = ""

    payload = (
        f"{ACCEPT_HEADER}\n"
        f"x-api-signature-nonce:{nonce}\n"
        f"x-api-signature-version:1.0\n"
        f"\n"
        f"{url_params}\n"
        f"{body_md5}\n"
        f"{timestamp}\n"
        f"{method}\n"
        f"{url}"
    )

    secret = INTL_SIGNING_SECRET if use_intl else EU_SIGNING_SECRET
    signature = base64.b64encode(
        hmac.new(secret, payload.encode("utf-8"), hashlib.sha1).digest()
    ).decode()
    return signature


def build_vc_signed_headers(
    method: str,
    url: str,
    account: Account,
) -> dict[str, str]:
    """Build Alibaba Cloud API Gateway signed headers for VC endpoints.

    The VC service (sg-app-api.smart.com/vc/) uses a different signing scheme
    from the vehicle data API: standard Alibaba Cloud API Gateway HmacSHA256.
    """
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query

    timestamp_ms = str(int(time.time() * 1000))
    # HTTP Date header: e.g. "Sat, 08 Mar 2026 09:00:00 GMT"
    date_str = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    nonce = str(uuid.uuid4())

    accept = "application/json;charset=UTF-8"
    content_type = "application/json;charset=UTF-8"

    # Build x-ca-* headers (sorted) for signature
    ca_headers = {
        "x-ca-key": INTL_X_CA_KEY,
        "x-ca-nonce": nonce,
        "x-ca-signature-method": "HmacSHA256",
        "x-ca-timestamp": timestamp_ms,
    }
    # Sorted header names for X-Ca-Signature-Headers
    sig_header_names = ",".join(sorted(ca_headers.keys()))

    # String to sign per Alibaba Cloud API Gateway spec:
    # METHOD\nAccept\nContent-MD5\nContent-Type\nDate\n
    # [sorted x-ca-* headers as key:value\n]
    # path[?query]
    lines = [
        method.upper(),
        accept,
        "",  # Content-MD5 (empty for GET)
        content_type,
        date_str,
    ]
    # Add sorted x-ca-* headers
    for k in sorted(ca_headers.keys()):
        lines.append(f"{k}:{ca_headers[k]}")
    # Add path with query
    resource = path
    if query:
        resource = f"{path}?{query}"
    lines.append(resource)

    string_to_sign = "\n".join(lines)

    signature = base64.b64encode(
        hmac.new(
            INTL_VC_APP_SECRET.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode()

    headers = {
        "accept": accept,
        "content-type": content_type,
        "date": date_str,
        "user-agent": "ALIYUN-ANDROID-DEMO",
        "x-ca-key": INTL_X_CA_KEY,
        "x-ca-nonce": nonce,
        "x-ca-timestamp": timestamp_ms,
        "x-ca-signature-method": "HmacSHA256",
        "x-ca-signature-headers": sig_header_names,
        "x-ca-signature": signature,
        "CA_VERSION": "1",
    }

    # Add x-smart-id (explicit in Retrofit annotation)
    if account.api_user_id:
        headers["x-smart-id"] = account.api_user_id

    # Add authorization (session access token)
    if account.api_access_token:
        headers["authorization"] = account.api_access_token

    # Xs-Auth-Token: idToken from INTL login (required by API gateway)
    if account.id_token:
        headers["Xs-Auth-Token"] = account.id_token

    return headers


def build_signed_headers(
    method: str,
    url: str,
    body: str | None,
    account: Account,
) -> dict[str, str]:
    """Build all required signed headers for a vehicle API request.

    Routes to region-specific header generation matching
    the pySmartHashtag reference implementation.
    """
    if account.region == Region.INTL:
        return _build_intl_headers(method, url, body, account)
    return _build_eu_headers(method, url, body, account)


def _build_eu_headers(
    method: str,
    url: str,
    body: str | None,
    account: Account,
) -> dict[str, str]:
    """Generate EU vehicle API headers (matching generate_default_header)."""
    parsed = urlparse(url)
    path = parsed.path
    params_str = parsed.query

    # EU uses dict-style params for signing
    params_dict: dict[str, str] = {}
    if params_str:
        for pair in params_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params_dict[k] = v

    timestamp = str(int(time.time() * 1000))
    nonce = secrets.token_hex(8)

    sign = _create_sign(nonce, params_dict, timestamp, method, path, body)

    headers = {
        "x-app-id": EU_APP_ID,
        "accept": ACCEPT_HEADER,
        "x-agent-type": "iOS",
        "x-device-type": "mobile",
        "x-operator-code": EU_OPERATOR_CODE,
        "x-device-identifier": account.device_id,
        "x-env-type": "production",
        "x-version": "smartNew",
        "accept-language": "en_US",
        "x-api-signature-version": "1.0",
        "x-api-signature-nonce": nonce,
        "x-device-manufacture": "Apple",
        "x-device-brand": "Apple",
        "x-device-model": "iPhone",
        "x-agent-version": "17.1",
        "content-type": "application/json; charset=utf-8",
        "user-agent": "Hello smart/1.4.0 (iPhone; iOS 17.1; Scale/3.00)",
        "x-signature": sign,
        "x-timestamp": timestamp,
    }
    if account.api_access_token:
        headers["authorization"] = account.api_access_token

    return headers


def _build_intl_headers(
    method: str,
    url: str,
    body: str | None,
    account: Account,
) -> dict[str, str]:
    """Generate INTL vehicle API headers (matching generate_intl_header)."""
    parsed = urlparse(url)
    path = parsed.path
    params_str = parsed.query

    params_dict: dict[str, str] = {}
    if params_str:
        for pair in params_str.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params_dict[k] = v

    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4()).upper()

    # INTL requires URL-encoded params in signature for GET requests
    url_encode_params = method.upper() == "GET"
    sign = _create_sign(
        nonce, params_dict, timestamp, method, path, body,
        use_intl=True, url_encode_params=url_encode_params,
    )

    headers = {
        "x-app-id": INTL_VEHICLE_APP_ID,
        "accept": ACCEPT_HEADER,
        "x-agent-type": "iOS",
        "x-device-type": "mobile",
        "x-operator-code": INTL_OPERATOR_CODE,
        "x-device-identifier": account.device_id,
        "x-env-type": "production",
        "accept-language": "en_US",
        "x-api-signature-version": "1.0",
        "x-api-signature-nonce": nonce,
        "x-device-manufacture": "Apple",
        "x-device-brand": "Apple",
        "x-device-model": "iPhone",
        "x-agent-version": "18.6.1",
        "content-type": "application/json",
        "user-agent": "GlobalSmart/1.0.7 (iPhone; iOS 18.6.1; Scale/3.00)",
        "x-signature": sign,
        "x-timestamp": timestamp,
        "platform": "NON-CMA",
        "x-vehicle-series": "HC1H2D3B6213-01_IL",
    }
    if account.api_access_token:
        headers["authorization"] = account.api_access_token
    if account.api_client_id:
        headers["x-client-id"] = account.api_client_id

    return headers


def _build_intl_session_headers(
    body: str,
    device_id: str,
) -> dict[str, str]:
    """Generate INTL headers for the session/secure exchange (step 3).

    Matches _generate_vehicle_api_headers from reference — no auth token yet.
    """
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4()).upper()

    sign = _create_sign(
        nonce=nonce,
        params={"identity_type": INTL_IDENTITY_TYPE},
        timestamp=timestamp,
        method="POST",
        url=API_SESSION_PATH,
        body=body,
        use_intl=True,
    )

    return {
        "x-app-id": INTL_VEHICLE_APP_ID,
        "x-operator-code": INTL_OPERATOR_CODE,
        "x-agent-type": "iOS",
        "x-agent-version": "18.6.1",
        "x-device-type": "mobile",
        "x-device-identifier": device_id,
        "x-device-manufacture": "Apple",
        "x-device-brand": "Apple",
        "x-device-model": "iPhone",
        "x-env-type": "production",
        "x-api-signature-version": "1.0",
        "x-api-signature-nonce": nonce,
        "x-timestamp": timestamp,
        "platform": "NON-CMA",
        "accept": ACCEPT_HEADER,
        "accept-language": "en_US",
        "content-type": "application/json",
        "user-agent": "GlobalSmart/1.0.7 (iPhone; iOS 18.6.1; Scale/3.00)",
        "x-signature": sign,
    }


async def async_login_intl(
    session: aiohttp.ClientSession,
    email: str,
    password: str,
) -> Account:
    """Authenticate against the Smart INTL API (3-step flow).

    Per contracts/smart-api.md INTL endpoints and research.md R2.
    """
    account = Account(
        username=email,
        region=Region.INTL,
        device_id=_generate_device_id(INTL_DEVICE_ID_LENGTH),
    )

    # Step 1: POST login
    login_url = f"{INTL_AUTH_BASE_URL}/iam/service/api/v1/login"
    login_headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json;charset=UTF-8",
        "X-Ca-Key": INTL_X_CA_KEY,
        "X-Ca-Nonce": str(uuid.uuid4()),
        "X-Ca-Timestamp": str(int(time.time() * 1000)),
        "X-App-Id": INTL_APP_ID,
        "User-Agent": "ALIYUN-ANDROID-DEMO",
    }
    login_body = json.dumps({"email": email, "password": password})

    async with session.post(
        login_url, data=login_body, headers=login_headers
    ) as resp:
        resp.raise_for_status()
        login_data = await resp.json()

    result = login_data.get("result", {})
    intl_access_token = result.get("accessToken", "")
    intl_id_token = result.get("idToken", "")
    intl_user_id = result.get("userId", "")
    expires_in = result.get("expiresIn", 86400)

    if not intl_access_token:
        _LOGGER.error("INTL login failed: no access token returned")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("INTL login failed: invalid credentials")

    _LOGGER.debug("INTL login step 1 complete for user")

    # Step 2: GET authorize
    authorize_url = (
        f"{INTL_AUTH_BASE_URL}/iam/service/api/v1/oauth20/authorize"
        f"?accessToken={intl_access_token}"
    )
    authorize_headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json;charset=UTF-8",
        "X-Ca-Key": INTL_X_CA_KEY,
        "X-Ca-Nonce": str(uuid.uuid4()),
        "X-Ca-Timestamp": str(int(time.time() * 1000)),
        "X-App-Id": INTL_APP_ID,
        "User-Agent": "ALIYUN-ANDROID-DEMO",
        "Xs-Auth-Token": intl_id_token,
    }

    async with session.get(authorize_url, headers=authorize_headers) as resp:
        resp.raise_for_status()
        auth_data = await resp.json()

    auth_code = auth_data.get("result", "")
    if not auth_code:
        _LOGGER.error("INTL authorize failed: no auth code returned")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("INTL authorize failed")

    _LOGGER.debug("INTL login step 2 complete (auth code obtained)")

    # Step 3: POST session exchange
    session_url = (
        f"{INTL_API_BASE_URL}{API_SESSION_PATH}"
        f"?identity_type={INTL_IDENTITY_TYPE}"
    )
    session_body_str = json.dumps({"authCode": auth_code})
    session_headers = _build_intl_session_headers(session_body_str, account.device_id)

    async with session.post(
        session_url, data=session_body_str, headers=session_headers
    ) as resp:
        resp.raise_for_status()
        session_data = await resp.json()

    if session_data.get("code") != 1000:
        _LOGGER.error("INTL session exchange failed: code=%s", session_data.get("code"))
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("INTL session exchange failed")

    data = session_data.get("data", {})
    account.api_access_token = data.get("accessToken", "")
    account.api_refresh_token = data.get("refreshToken", "")
    account.api_user_id = data.get("userId", "")
    account.api_client_id = data.get("clientId", "")
    account.access_token = intl_access_token
    account.id_token = intl_id_token
    account.state = AuthState.AUTHENTICATED

    from datetime import datetime, timedelta

    account.expires_at = datetime.now() + timedelta(seconds=expires_in)

    _LOGGER.debug("INTL login complete — session established")
    return account


async def async_login_eu(
    session: aiohttp.ClientSession,
    email: str,
    password: str,
) -> Account:
    """Authenticate against the Smart EU API (4-step Gigya flow).

    Per contracts/smart-api.md EU endpoints and research.md R1.
    """
    account = Account(
        username=email,
        region=Region.EU,
        device_id=_generate_device_id(EU_DEVICE_ID_LENGTH),
    )

    # Step 1: GET context
    context_url = (
        f"{EU_CONTEXT_URL}/login-app/api/v1/authorize?uiLocales=de-DE"
    )
    context_headers = {
        "x-app-id": EU_APP_ID,
        "x-requested-with": "com.smart.hellosmart",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "user-agent": EU_WEBVIEW_USER_AGENT,
    }

    # Walk the OIDC redirect chain looking for the first hop whose Location
    # contains ?context=. Smart's chain currently looks like:
    #   awsapi.future.smart.com -> auth.smart.com/oidc/.../authorize
    #     -> app.id.smart.com/proxy?context=<JWT>&...
    # The context= used to be on hop 1; it moved to hop 2 (different host).
    # Walking up to MAX_HOPS keeps this resilient if Smart shifts hops again.
    MAX_HOPS = 5
    current_url = context_url
    context: str | None = None
    last_status: int | None = None
    last_location = ""
    for hop in range(MAX_HOPS):
        async with session.get(
            current_url, headers=context_headers, allow_redirects=False
        ) as resp:
            last_status = resp.status
            if resp.status not in (301, 302, 303, 307, 308):
                if hop == 0 and resp.status == 403:
                    _LOGGER.error(
                        "EU auth gateway rejected request "
                        "(HTTP 403): possible UA filtering or API change"
                    )
                else:
                    _LOGGER.error(
                        "EU context redirect chain ended at hop %d "
                        "with non-redirect status=%s",
                        hop,
                        resp.status,
                    )
                account.state = AuthState.AUTH_FAILED
                raise AuthenticationError(
                    f"EU context request failed: HTTP {resp.status}"
                )
            last_location = resp.headers.get("Location", "")

        parsed_location = urlparse(last_location)
        params = parse_qs(parsed_location.query)
        if "context" in params:
            context = params["context"][0]
            _LOGGER.debug(
                "EU login step 1: extracted context= at redirect hop %d "
                "(host=%s)",
                hop + 1,
                parsed_location.hostname or "?",
            )
            break
        current_url = last_location

    if not context:
        _LOGGER.error(
            "EU context extraction failed: redirect chain ended without "
            "context= parameter (last_status=%s, last_location_host=%s)",
            last_status,
            urlparse(last_location).hostname or "?",
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError(
            "EU context extraction failed: redirect chain ended without "
            "context= parameter"
        )

    _LOGGER.debug("EU login step 1 complete (context obtained)")

    # Step 1.5: fetch Gigya machine identifiers (gmid + ucid).
    #
    # Smart's Gigya tenant won't accept accounts.login from a "fresh"
    # client; it expects a bootstrapped Gigya session (gmid+ucid+
    # hasGmid+gig_bootstrap cookies). socialize.getIDs is the canonical
    # endpoint that issues these to a JS-SDK client. We send them in
    # the Cookie header on Step 2 and Step 3.
    ids_url = (
        f"{EU_GIGYA_SOCIALIZE_BASE}/socialize.getIDs"
        f"?APIKey={GIGYA_API_KEY}&format=json&includeTicket=true"
    )
    async with session.get(ids_url) as resp:
        resp.raise_for_status()
        ids_data = await resp.json(content_type=None)

    if ids_data.get("errorCode") != 0:
        _LOGGER.error(
            "EU socialize.getIDs failed: code=%s message=%s",
            ids_data.get("errorCode"),
            ids_data.get("errorMessage"),
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError(
            "EU socialize.getIDs failed: cannot bootstrap Gigya session"
        )

    gmid = ids_data.get("gmid", "")
    ucid = ids_data.get("ucid", "")
    if not gmid:
        _LOGGER.error("EU socialize.getIDs returned no gmid")
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError("EU Gigya gmid missing — cannot proceed")

    # Cookie header that declares the SDK has bootstrapped a Gigya
    # session. gig_bootstrap_<APIKey>=auth_ver4 is the literal value
    # the JS SDK sets to mark "Gigya bootstrap complete, login allowed".
    gigya_cookie_base = (
        f"gmid={gmid}; ucid={ucid}; hasGmid=ver4; "
        f"gig_bootstrap_{GIGYA_API_KEY}=auth_ver4"
    )
    _LOGGER.debug("EU login step 1.5 complete (Gigya bootstrap cookies built)")

    # Step 2: POST Gigya login.
    #
    # Smart's Gigya rejects accounts.login without the bootstrap cookie
    # (returns 400006 "request is blocked because of security issues").
    # With the bootstrap cookie in place, sdk=js_latest is accepted again,
    # which matches what the Hello Smart Android webview sends.
    gigya_url = f"{EU_AUTH_BASE_URL}/accounts.login"
    gigya_body = urlencode(
        {
            "loginID": email,
            "password": password,
            "sessionExpiration": "2592000",
            "targetEnv": "jssdk",
            "include": "profile,data,emails,subscriptions,preferences,",
            "includeUserInfo": "True",
            "loginMode": "standard",
            "lang": "de",
            "APIKey": GIGYA_API_KEY,
            "source": "showScreenSet",
            "sdk": "js_latest",
            "sdkBuild": "15482",
            "format": "json",
            "pageURL": "https://app.id.smart.com/login?gig_ui_locales=de-DE",
        }
    )
    gigya_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "accept-language": "de",
        "origin": "https://app.id.smart.com",
        "x-requested-with": "com.smart.hellosmart",
        "user-agent": EU_WEBVIEW_USER_AGENT,
        "cookie": gigya_cookie_base,
    }

    async with session.post(gigya_url, data=gigya_body, headers=gigya_headers) as resp:
        resp.raise_for_status()
        gigya_data = await resp.json(content_type=None)

    # Gigya returns 200 even on errors
    if "errorCode" in gigya_data and gigya_data["errorCode"] != 0:
        gigya_code = gigya_data.get("errorCode")
        gigya_message = gigya_data.get("errorMessage", "")
        gigya_details = gigya_data.get("errorDetails", "")
        # Gigya 4xxxxx codes are credential / account errors; everything else
        # is upstream (rate-limit, API key invalid, schema, etc.).
        is_credential_error = (
            isinstance(gigya_code, int) and 400000 <= gigya_code < 500000
        )
        _LOGGER.error(
            "EU Gigya login error: code=%s message=%s details=%s",
            gigya_code,
            gigya_message,
            gigya_details,
        )
        account.state = AuthState.AUTH_FAILED
        if is_credential_error:
            raise AuthenticationError(
                f"EU Gigya rejected credentials (code={gigya_code}): "
                f"{gigya_message}"
            )
        raise AuthenticationError(
            f"EU Gigya login error (code={gigya_code}): {gigya_message}"
        )

    session_info = gigya_data.get("sessionInfo", {})
    login_token = session_info.get("login_token", "")
    # Gigya returns expires_in as a string ("3600"); coerce so the
    # later timedelta() call doesn't blow up.
    try:
        expires_in = int(session_info.get("expires_in", 3600))
    except (TypeError, ValueError):
        expires_in = 3600

    if not login_token:
        _LOGGER.error(
            "EU Gigya login returned no login_token; payload keys=%s",
            list(gigya_data.keys()),
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError(
            "EU Gigya login succeeded but returned no login_token"
        )

    _LOGGER.debug("EU login step 2 complete (login_token obtained)")

    # Step 3: GET authorize/continue and walk its redirect chain.
    #
    # Smart returns the OAuth tokens on the LAST hop of a 2-hop chain,
    # in the URL's *query string* (not fragment). Earlier flows used
    # the implicit fragment form (#access_token=...) — handle both for
    # forward compatibility.
    #
    # The /authorize/continue handler authenticates the request via
    # cookies, not query params: the Gigya bootstrap cookie (gmid +
    # ucid + hasGmid + gig_bootstrap) PLUS the session cookie
    # glt_<APIKey>=<login_token>. With those, no DeviceId / gmidTicket
    # / sig query parameters are required.
    authorize_url = (
        f"{EU_AUTH_BASE_URL}/oidc/op/v1.0/{GIGYA_API_KEY}/authorize/continue"
        f"?context={context}&login_token={login_token}"
    )
    authorize_cookie = (
        f"{gigya_cookie_base}; "
        f"glt_{GIGYA_API_KEY}={login_token}"
    )
    authorize_headers = {
        "accept": "*/*",
        "accept-language": "de-DE,de;q=0.9,en-DE;q=0.8,en-US;q=0.7,en;q=0.6",
        "x-requested-with": "com.smart.hellosmart",
        "user-agent": EU_WEBVIEW_USER_AGENT,
        "cookie": authorize_cookie,
    }

    eu_access_token: str | None = None
    eu_refresh_token: str | None = None
    current_url = authorize_url
    last_status: int | None = None
    last_location = ""
    last_content_type = ""
    last_body = ""
    for hop in range(MAX_HOPS):
        async with session.get(
            current_url, headers=authorize_headers, allow_redirects=False
        ) as resp:
            last_status = resp.status
            last_location = resp.headers.get("Location", "")
            last_content_type = resp.headers.get("Content-Type", "")
            try:
                last_body = await resp.text()
            except Exception:  # noqa: BLE001
                last_body = "<unreadable>"

        _LOGGER.debug(
            "EU step 3 hop %d: status=%s content-type=%s "
            "location=%s body=%s",
            hop,
            last_status,
            last_content_type,
            _redact(last_location, limit=512),
            _redact(last_body, limit=512),
        )

        if last_status not in (301, 302, 303, 307, 308):
            break

        parsed_redirect = urlparse(last_location)
        fragment_params = parse_qs(parsed_redirect.fragment)
        query_params = parse_qs(parsed_redirect.query)

        # Smart surfaces auth errors via a redirect to /proxy?mode=error
        if query_params.get("mode", [None])[0] == "error":
            err_code = query_params.get("errorCode", [""])[0]
            err_msg = query_params.get("errorMessage", [""])[0]
            _LOGGER.error(
                "EU authorize/continue redirected to error page: "
                "code=%s message=%s",
                err_code,
                err_msg,
            )
            account.state = AuthState.AUTH_FAILED
            raise AuthenticationError(
                f"EU authorize/continue error (code={err_code}): {err_msg}"
            )

        eu_access_token = (
            query_params.get("access_token", [None])[0]
            or fragment_params.get("access_token", [None])[0]
        )
        eu_refresh_token = (
            query_params.get("refresh_token", [None])[0]
            or fragment_params.get("refresh_token", [None])[0]
        )
        if eu_access_token:
            _LOGGER.debug(
                "EU step 3: access_token extracted from redirect hop %d "
                "(host=%s, source=%s)",
                hop + 1,
                parsed_redirect.hostname or "?",
                "query" if query_params.get("access_token") else "fragment",
            )
            break

        # No access_token yet — follow this hop and try again.
        current_url = last_location

    if not eu_access_token:
        _LOGGER.error(
            "EU access token extraction failed after %d hops; "
            "last_status=%s last_host=%s",
            MAX_HOPS,
            last_status,
            urlparse(last_location).hostname or "?",
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError(
            "EU access token extraction failed: walked redirect chain "
            "without finding access_token"
        )

    _LOGGER.debug("EU login step 3 complete (access_token obtained)")

    # Step 4: POST session exchange.
    #
    # Pre-serialize the body once with stdlib json.dumps and POST it via
    # data=<str> rather than json=<dict>. The signature is computed over
    # the exact bytes we send; passing json=<dict> lets aiohttp re-encode
    # later (and HA's shared session swaps stdlib json for orjson, which
    # omits spaces — producing different bytes than what we signed and
    # tripping the cloud's "Check signature error" code 1445).
    session_url = (
        f"{EU_API_BASE_URL}/auth/account/session/secure"
        f"?identity_type={EU_IDENTITY_TYPE}"
    )
    session_body_str = json.dumps({"accessToken": eu_access_token})

    signed_headers = build_signed_headers(
        "POST",
        session_url,
        session_body_str,
        Account(
            username=email,
            region=Region.EU,
            device_id=account.device_id,
            api_access_token=eu_access_token,
        ),
    )

    async with session.post(
        session_url, data=session_body_str, headers=signed_headers
    ) as resp:
        resp.raise_for_status()
        session_data = await resp.json()

    if session_data.get("code") != 1000:
        _LOGGER.error(
            "EU session exchange failed: code=%s message=%s",
            session_data.get("code"),
            session_data.get("message"),
        )
        account.state = AuthState.AUTH_FAILED
        raise AuthenticationError(
            f"EU session exchange failed (code={session_data.get('code')}): "
            f"{session_data.get('message')}"
        )

    data = session_data.get("data", {})
    account.api_access_token = data.get("accessToken", "")
    account.api_refresh_token = data.get("refreshToken", "")
    account.api_user_id = data.get("userId", "")
    account.access_token = eu_access_token
    account.state = AuthState.AUTHENTICATED

    from datetime import datetime, timedelta

    account.expires_at = datetime.now() + timedelta(seconds=expires_in)

    _LOGGER.debug("EU login complete — session established")
    return account


class AuthenticationError(Exception):
    """Raised when Smart API authentication fails."""
