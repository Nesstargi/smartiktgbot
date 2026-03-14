from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from bot.runtime import (
    get_webhook_path,
    is_webhook_mode,
    process_webhook_update,
    webhook_secret_is_valid,
)

router = APIRouter()

TELEGRAM_WEBHOOK_ROUTE = get_webhook_path()


@router.post(TELEGRAM_WEBHOOK_ROUTE, status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(
        default=None,
        alias="X-Telegram-Bot-Api-Secret-Token",
    ),
):
    if not is_webhook_mode():
        raise HTTPException(status_code=404, detail="Webhook is not enabled")

    if not webhook_secret_is_valid(x_telegram_bot_api_secret_token):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    payload = await request.json()
    try:
        await process_webhook_update(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_200_OK)
