# Payments / Monetization

Configuration (in `.env.*`):
- `MONETIZATION_ENABLED=true|false`
- `PRICE_PER_POST=integer`
- `PAYMENT_PROVIDER=mock|yookassa|qiwi` (currently only `mock` is implemented)

Flow:
1. User creates ad. If monetization enabled, the ad status becomes `awaiting_payment` and `payment_id` is set.
2. User performs payment (mock flow: use `/pay_confirm <ad_id>` command in client bot to confirm).
3. After payment verification, ad is marked `is_paid=True` and status becomes `pending` (sent to moderators).

Payment provider adapter: `app.services.payments` — implement new provider that matches `PaymentProvider` protocol to integrate real providers.
