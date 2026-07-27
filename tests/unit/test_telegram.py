import pytest
import httpx
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.notifications.telegram.client import TelegramClient
from app.modules.notifications.telegram.service import TelegramNotificationService
from app.modules.notifications.telegram.templates import TelegramTemplates, NotificationType
from app.modules.notifications.telegram.exceptions import (
    TelegramBaseError,
    TelegramNetworkError,
    TelegramAPIError,
    TelegramRateLimitError,
    TelegramAuthError,
    TelegramBadRequestError
)

def test_telegram_rate_limit_error():
    err = TelegramRateLimitError("Too Many Requests", retry_after=42)
    assert err.retry_after == 42
    assert str(err) == "Too Many Requests"

def test_templates_escaping():
    text, category = TelegramTemplates.new_product("<script>alert(1)</script>", "http://test.com/&id=1")
    assert "&lt;script&gt;" in text
    assert "http://test.com/&amp;id=1" in text
    assert category == NotificationType.SUCCESS

def test_templates_target_price_reached():
    text, category = TelegramTemplates.target_price_reached("Laptop", "http://url", Decimal("900"), Decimal("1000"), "USD")
    assert category == NotificationType.SUCCESS
    assert "900 USD" in text

def test_templates_price_drop():
    text, category = TelegramTemplates.price_drop("Laptop", "http://url", Decimal("1000"), Decimal("800"), "USD")
    assert category == NotificationType.INFO
    assert "800 USD" in text

def test_templates_parsing_error():
    text, category = TelegramTemplates.parsing_error(1, "http://url", "Timeout")
    assert category == NotificationType.ERROR
    assert "Timeout" in text

def test_templates_critical_error():
    text, category = TelegramTemplates.critical_error("DB Down", "Connection refused")
    assert category == NotificationType.CRITICAL
    assert "DB Down" in text

def test_templates_parsing_finished():
    text, category = TelegramTemplates.parsing_finished(10, 2)
    assert category == NotificationType.INFO
    assert "10" in text and "2" in text

@pytest.mark.asyncio
async def test_client_missing_token():
    client = TelegramClient()
    with patch("app.modules.notifications.telegram.client.settings.telegram_bot_token", None):
        res = await client._make_request.__wrapped__(client, "testMethod", {})
        assert res == {}

@pytest.mark.asyncio
async def test_client_make_request_200():
    client = TelegramClient()
    mock_token = MagicMock()
    mock_token.get_secret_value.return_value = "fake_token"
    
    with patch("app.modules.notifications.telegram.client.settings.telegram_bot_token", mock_token), \
         patch("app.modules.notifications.telegram.client.httpx.AsyncClient") as mock_httpx:
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True, "result": "msg"}
        
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_resp
        mock_httpx.return_value.__aenter__.return_value = mock_instance
        
        res = await client._make_request.__wrapped__(client, "sendMessage", {})
        assert res == {"ok": True, "result": "msg"}

@pytest.mark.asyncio
async def test_client_make_request_429_rate_limit():
    client = TelegramClient()
    mock_token = MagicMock()
    mock_token.get_secret_value.return_value = "fake_token"
    
    with patch("app.modules.notifications.telegram.client.settings.telegram_bot_token", mock_token), \
         patch("app.modules.notifications.telegram.client.httpx.AsyncClient") as mock_httpx:
        
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.headers = {"Retry-After": "15"}
        
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_resp
        mock_httpx.return_value.__aenter__.return_value = mock_instance
        
        with pytest.raises(TelegramRateLimitError) as exc:
            await client._make_request.__wrapped__(client, "sendMessage", {})
        assert exc.value.retry_after == 15

@pytest.mark.asyncio
@pytest.mark.parametrize("status_code, expected_exc", [
    (401, TelegramAuthError),
    (404, TelegramAuthError),
    (400, TelegramBadRequestError),
])
async def test_client_make_request_auth_and_bad_requests(status_code, expected_exc):
    client = TelegramClient()
    mock_token = MagicMock()
    mock_token.get_secret_value.return_value = "fake_token"
    
    with patch("app.modules.notifications.telegram.client.settings.telegram_bot_token", mock_token), \
         patch("app.modules.notifications.telegram.client.httpx.AsyncClient") as mock_httpx:
        
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.text = "Error detail"
        
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_resp
        mock_httpx.return_value.__aenter__.return_value = mock_instance
        
        with pytest.raises(expected_exc):
            await client._make_request.__wrapped__(client, "sendMessage", {})

@pytest.mark.asyncio
async def test_client_make_request_http_status_error():
    client = TelegramClient()
    mock_token = MagicMock()
    mock_token.get_secret_value.return_value = "fake_token"
    
    with patch("app.modules.notifications.telegram.client.settings.telegram_bot_token", mock_token), \
         patch("app.modules.notifications.telegram.client.httpx.AsyncClient") as mock_httpx:
        
        mock_instance = AsyncMock()
        req = httpx.Request("POST", "http://test")
        resp = httpx.Response(500, request=req, text="Internal Server Error")
        mock_instance.post.side_effect = httpx.HTTPStatusError("500", request=req, response=resp)
        mock_httpx.return_value.__aenter__.return_value = mock_instance
        
        with pytest.raises(TelegramAPIError):
            await client._make_request.__wrapped__(client, "sendMessage", {})

@pytest.mark.asyncio
async def test_client_make_request_network_error():
    client = TelegramClient()
    mock_token = MagicMock()
    mock_token.get_secret_value.return_value = "fake_token"
    
    with patch("app.modules.notifications.telegram.client.settings.telegram_bot_token", mock_token), \
         patch("app.modules.notifications.telegram.client.httpx.AsyncClient") as mock_httpx:
        
        mock_instance = AsyncMock()
        req = httpx.Request("POST", "http://test")
        mock_instance.post.side_effect = httpx.RequestError("Network down", request=req)
        mock_httpx.return_value.__aenter__.return_value = mock_instance
        
        with pytest.raises(TelegramNetworkError):
            await client._make_request.__wrapped__(client, "sendMessage", {})

@pytest.mark.asyncio
async def test_client_wrappers():
    client = TelegramClient()
    with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_make:
        mock_make.return_value = {"ok": True}
        
        await client.send_message(123, "Test")
        mock_make.assert_called_with("sendMessage", {"chat_id": 123, "text": "Test"})
        
        await client.send_photo(123, "http://photo", "Caption")
        mock_make.assert_called_with("sendPhoto", {"chat_id": 123, "photo": "http://photo", "caption": "Caption"})

@pytest.mark.asyncio
async def test_service_no_chat_id():
    service = TelegramNotificationService()
    service._chat_id = None
    with patch.object(service._client, "send_message", new_callable=AsyncMock) as mock_send:
        await service._send_notification("Test")
        mock_send.assert_not_called()

@pytest.mark.asyncio
async def test_service_send_notification_success():
    service = TelegramNotificationService()
    service._chat_id = "12345"
    with patch.object(service._client, "send_message", new_callable=AsyncMock) as mock_send:
        await service._send_notification("Test Msg")
        mock_send.assert_called_once_with(
            chat_id="12345", 
            text="Test Msg", 
            parse_mode="HTML", 
            disable_web_page_preview=True
        )

@pytest.mark.asyncio
async def test_service_send_notification_telegram_error():
    service = TelegramNotificationService()
    service._chat_id = "12345"
    with patch.object(service._client, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = TelegramBaseError("TG Error")
        await service._send_notification("Test Msg") 

@pytest.mark.asyncio
async def test_service_send_notification_generic_error():
    service = TelegramNotificationService()
    service._chat_id = "12345"
    with patch.object(service._client, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = ValueError("Generic Error")
        await service._send_notification("Test Msg")

@pytest.mark.asyncio
async def test_service_notify_methods():
    service = TelegramNotificationService()
    with patch.object(service, "_send_notification", new_callable=AsyncMock) as mock_send:
        await service.notify_price_drop("P1", "http", Decimal("10"), Decimal("15"), "BYN")
        mock_send.assert_called_once()
        assert "P1" in mock_send.call_args[0][0]
        
        mock_send.reset_mock()
        await service.notify_parsing_error(99, "http", "Timeout")
        mock_send.assert_called_once()
        assert "99" in mock_send.call_args[0][0]
