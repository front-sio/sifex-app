# TCRA Dokploy Setup (Web + Celery)

Use identical TCRA mounts and env vars on both services:
- `web` (gunicorn/Django)
- `celery` worker

Do not commit `.pfx` files to git. This repository ignores `*.pfx` and `*.p12`.

## Host Secret File

Create the host path and permissions exactly:

```bash
sudo mkdir -p /opt/sifongo/secrets/tcra/prod
sudo cp TCRAPOSTSprivate.pfx /opt/sifongo/secrets/tcra/prod/private.pfx
sudo chown root:sifongo /opt/sifongo/secrets/tcra/prod /opt/sifongo/secrets/tcra/prod/private.pfx
sudo chmod 750 /opt/sifongo/secrets/tcra/prod
sudo chmod 640 /opt/sifongo/secrets/tcra/prod/private.pfx
```

## Dokploy Volume Mount

Add this same read-only mount to both `web` and `celery`:

`/opt/sifongo/secrets/tcra/prod/private.pfx:/run/secrets/tcra_private.pfx:ro`

## Dokploy Environment Variables

Set in Dokploy variables:
- `TCRA_PFX_PASSWORD`
- `TCRA_BASE_URL`

Set in both services (`web` and `celery`):
- `TCRA_PFX_PATH=/run/secrets/tcra_private.pfx`
- `TCRA_SIGNATURE_HEADER=X-TCRA-Signature`
- `TCRA_OPERATOR_CODE=1004`

Webhook public verification key/cert (at least one required):
- `TCRA_WEBHOOK_PUBLIC_CERT_PATH` or `TCRA_WEBHOOK_PUBLIC_CERT_B64` or `TCRA_WEBHOOK_PUBLIC_CERT_PEM`
- or `TCRA_WEBHOOK_PUBLIC_KEY_PATH` or `TCRA_WEBHOOK_PUBLIC_KEY_B64` or `TCRA_WEBHOOK_PUBLIC_KEY_PEM`

## Runtime Behavior

- Outbound requests are signed from PKCS#12 private key loaded from `TCRA_PFX_PATH`.
- Private key is cached in-memory after first load.
- JSON signing input uses stable serialization: `separators=(",", ":")`, UTF-8 bytes.
- `Content-Type` is always `application/json`.
- Signature is sent in `TCRA_SIGNATURE_HEADER`.
- Webhook requests with missing/invalid signature return `401`.
- Invalid webhook signatures are never enqueued for Celery processing.
- In production (`DEBUG=False`), startup fails if PKCS#12 config is missing/invalid.

## Host Verification Commands

```bash
sudo stat -c '%U:%G %a %n' /opt/sifongo/secrets/tcra/prod /opt/sifongo/secrets/tcra/prod/private.pfx
```

Expected:
- `/opt/sifongo/secrets/tcra/prod` => `root:sifongo 750`
- `/opt/sifongo/secrets/tcra/prod/private.pfx` => `root:sifongo 640`
