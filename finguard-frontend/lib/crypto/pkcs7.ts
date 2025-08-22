export function pkcs7Pad(data: Uint8Array, blockSize = 16): Uint8Array {
  const padLen = blockSize - (data.length % blockSize)
  const out = new Uint8Array(data.length + padLen)
  out.set(data, 0)
  out.fill(padLen, data.length)
  return out
}

export function pkcs7Unpad(data: Uint8Array, blockSize = 16): Uint8Array {
  if (data.length === 0 || data.length % blockSize !== 0) throw new Error("Invalid PKCS#7 block size")
  const padLen = data[data.length - 1]
  if (padLen <= 0 || padLen > blockSize) throw new Error("Invalid PKCS#7 padding length")
  for (let i = data.length - padLen; i < data.length; i++) {
    if (data[i] !== padLen) throw new Error("Bad PKCS#7 padding")
  }
  return data.subarray(0, data.length - padLen)
}
