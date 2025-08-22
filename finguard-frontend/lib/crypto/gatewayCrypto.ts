import { pemToArrayBuffer } from "./pem"
import { pkcs7Pad, pkcs7Unpad } from "./pkcs7"
import { base64ToBytes, bytesToBase64 } from "./base64"

const enc = new TextEncoder()
const dec = new TextDecoder()

export type EncryptedPayload = {
  encrypted_data: string
  encrypted_key: string
  iv: string
}

let cachedGatewayPublicKey: CryptoKey | null = null
let cachedClientPrivateKey: CryptoKey | null = null

export async function loadGatewayPublicKey(): Promise<CryptoKey> {
  if (cachedGatewayPublicKey) return cachedGatewayPublicKey

  const res = await fetch("/api/gateway/public-key") // proxied to the gateway
  if (!res.ok) {
    console.error("[v0] Failed to fetch gateway public key:", res.status, res.statusText)
    throw new Error(`Failed to fetch gateway public key: ${res.status} ${res.statusText}`)
  }

  try {
    const { public_key } = await res.json()
    const spkiDer = pemToArrayBuffer(public_key)
    cachedGatewayPublicKey = await crypto.subtle.importKey(
      "spki",
      spkiDer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      false,
      ["encrypt"],
    )
    console.log("[v0] Successfully loaded gateway public key")
    return cachedGatewayPublicKey
  } catch (error) {
    console.error("[v0] Error processing gateway public key:", error)
    throw new Error("Failed to process gateway public key")
  }
}

export async function loadClientPrivateKey(): Promise<CryptoKey> {
  if (cachedClientPrivateKey) return cachedClientPrivateKey
  // Dev-only: private key is served from /public/keys/client_private_key.pem
  const res = await fetch("/keys/client_private_key.pem")
  if (!res.ok) {
    console.error("[v0] Failed to fetch client private key:", res.status, res.statusText)
    throw new Error(`Missing /keys/client_private_key.pem: ${res.status} ${res.statusText}`)
  }

  try {
    const pem = await res.text()
    const pkcs8Der = pemToArrayBuffer(pem)
    cachedClientPrivateKey = await crypto.subtle.importKey(
      "pkcs8",
      pkcs8Der,
      { name: "RSA-OAEP", hash: "SHA-256" },
      false,
      ["decrypt"],
    )
    console.log("[v0] Successfully loaded client private key")
    return cachedClientPrivateKey
  } catch (error) {
    console.error("[v0] Error processing client private key:", error)
    throw new Error("Failed to process client private key")
  }
}

function randomBytes(len: number): Uint8Array {
  const b = new Uint8Array(len)
  crypto.getRandomValues(b)
  return b
}

export async function encryptRequestBody(data: any): Promise<EncryptedPayload> {
  const gatewayKey = await loadGatewayPublicKey()
  const jsonBytes = enc.encode(JSON.stringify(data))

  // AES256 key + IV
  const aesKeyBytes = randomBytes(32)
  const iv = randomBytes(16)

  // AES-CBC with manual PKCS7
  const padded = pkcs7Pad(jsonBytes, 16)
  const aesKey = await crypto.subtle.importKey("raw", aesKeyBytes, { name: "AES-CBC", length: 256 }, false, ["encrypt"])
  const ciphertext = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-CBC", iv }, aesKey, padded))

  // Wrap the AES key with RSA-OAEP(SHA-256)
  const wrappedKey = new Uint8Array(await crypto.subtle.encrypt({ name: "RSA-OAEP" }, gatewayKey, aesKeyBytes))

  return {
    encrypted_data: bytesToBase64(ciphertext),
    encrypted_key: bytesToBase64(wrappedKey),
    iv: bytesToBase64(iv),
  }
}

export async function decryptResponseBody(payload: EncryptedPayload): Promise<any> {
  const privateKey = await loadClientPrivateKey()
  const encData = base64ToBytes(payload.encrypted_data)
  const encKey = base64ToBytes(payload.encrypted_key)
  const iv = base64ToBytes(payload.iv)

  // Unwrap AES key with RSA-OAEP(SHA-256)
  const aesKeyBytes = new Uint8Array(await crypto.subtle.decrypt({ name: "RSA-OAEP" }, privateKey, encKey))

  const aesKey = await crypto.subtle.importKey("raw", aesKeyBytes, { name: "AES-CBC", length: 256 }, false, ["decrypt"])

  const padded = new Uint8Array(await crypto.subtle.decrypt({ name: "AES-CBC", iv }, aesKey, encData))

  const unpadded = pkcs7Unpad(padded, 16)
  const json = dec.decode(unpadded)
  return JSON.parse(json)
}
