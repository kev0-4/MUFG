# FinGuard Frontend (E2E Encrypted)

## Prereqs
- Node 18+
- FinGuard API Gateway running on http://localhost:8080

## Setup
1. Copy `.env.local` and set `NEXT_PUBLIC_API_GATEWAY_BASE_URL=http://localhost:8080`.
2. Place your **dev** private key at `public/keys/client_private_key.pem` (PKCS#8 PEM). This must match the public key stored at the API gateway as `keys/client_public_key.pem`.
3. Install deps: `npm install`.
4. Run: `npm run dev` and open http://localhost:3000.

## Notes
- All requests are encrypted client-side with AES-256-CBC + PKCS#7 and the AES key is wrapped with RSA-OAEP(SHA-256).
- The gateway response is decrypted client-side using the dev private key.
- A Next.js server route proxies requests to the gateway to avoid CORS.

## Usage
- **Dashboard**: User data, simulations, and recommendations
- **Stocks**: Latest stock data and historical data queries
- **NLP**: Stock sentiments, AI enhancement, and general queries

The app will show "Crypto ready" when both the gateway public key and client private key are loaded successfully.
\`\`\`

```pem file="public/keys/client_private_key.pem"
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5+example+key+
content+here+this+is+a+placeholder+private+key+that+needs+to+be+replaced+with+
the+actual+dev+private+key+that+matches+the+public+key+on+the+gateway+server+
for+proper+RSA+OAEP+decryption+to+work+correctly+in+the+application
-----END PRIVATE KEY-----
