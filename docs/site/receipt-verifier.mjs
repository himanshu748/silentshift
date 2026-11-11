// Verifies the owned Java receipt format locally; never grants routing authority.
export const MAX_RECEIPT_BYTES = 65536;
export const canonical = (value) => JSON.stringify(value, (_, item) => {
  if (item && typeof item === 'object' && !Array.isArray(item))
    return Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]]));
  return item;
});

// Match the native exporter's rejection of duplicate JSON fields and trailing data.
export function strictJSON(text) {
  if (typeof text !== 'string' || new TextEncoder().encode(text).length > MAX_RECEIPT_BYTES)
    throw new Error('Use a UTF-8 receipt no larger than 64 KiB.');
  let offset = 0;
  const space = () => { while (/[ \t\r\n]/.test(text[offset] || '') && offset < text.length) offset++; };
  const string = () => {
    const start = offset++;
    while (offset < text.length) {
      const char = text[offset++];
      if (char === '\\') { offset++; continue; }
      if (char === '"') return JSON.parse(text.slice(start, offset));
    }
    throw new Error('Unterminated JSON string.');
  };
  const value = (depth = 0) => {
    if (depth > 10) throw new Error('Receipt nesting exceeds the format limit.');
    space(); const char = text[offset];
    if (char === '"') return string();
    if (char === '{' || char === '[') {
      const object = char === '{', result = object ? Object.create(null) : [];
      const end = object ? '}' : ']'; offset++; space();
      if (text[offset] === end) { offset++; return result; }
      while (offset < text.length) {
        space(); let key;
        if (object) {
          if (text[offset] !== '"') throw new Error('Expected a JSON field name.');
          key = string(); space();
          if (Object.hasOwn(result, key)) throw new Error('Duplicate JSON field: ' + key);
          if (text[offset++] !== ':') throw new Error('Expected a field separator.');
        }
        const item = value(depth + 1);
        if (object) result[key] = item; else result.push(item);
        space(); const separator = text[offset++];
        if (separator === end) return result;
        if (separator !== ',') throw new Error('Expected a JSON item separator.');
      }
      throw new Error('Incomplete receipt JSON.');
    }
    const match = /^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(text.slice(offset));
    if (!match) throw new Error('Invalid receipt JSON.');
    offset += match[0].length; const result = JSON.parse(match[0]);
    if (typeof result === 'number' && !Number.isFinite(result)) throw new Error('Non-finite JSON number.');
    return result;
  };
  const result = value(); space();
  if (offset !== text.length) throw new Error('Trailing content after receipt JSON.');
  return result;
}

const exact = (value, keys) => value && !Array.isArray(value) && typeof value === 'object'
  && Object.keys(value).sort().join(',') === [...keys].sort().join(',');
const hex = bytes => Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, '0')).join('');
const base64 = text => {
  if (typeof text !== 'string' || text.length > 4096 || !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(text))
    throw new Error('Invalid signature or public-key encoding.');
  return Uint8Array.from(atob(text), char => char.charCodeAt(0));
};

export async function verifyReceipt(text, expectedFingerprint = '') {
  if (!globalThis.crypto?.subtle) throw new Error('Local verification needs Web Crypto: use HTTPS or localhost.');
  const node = strictJSON(text), signed = node?.signed, payload = signed?.payload;
  if (!exact(node, ['public_key_spki', 'signature', 'signature_algorithm', 'signed'])
    || node.signature_algorithm !== 'SHA256withRSA'
    || !exact(signed, ['created_at', 'payload', 'schema', 'sha256'])
    || signed.schema !== 'silentshift-java-pex/1'
    || !exact(payload, ['case_id', 'decision', 'evidence_hashes', 'execution_mode', 'synthetic']))
    throw new Error('This is not the supported Java PEX receipt format.');
  if (typeof payload.case_id !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(payload.case_id)
    || !['DELIVERED', 'QUARANTINED', 'REVIEW', 'REJECTED'].includes(payload.decision)
    || !['live', 'recorded-replay'].includes(payload.execution_mode)
    || typeof payload.synthetic !== 'boolean'
    || typeof signed.created_at !== 'string' || !/^\d{4}-\d\d-\d\dT[\d:.]+Z$/.test(signed.created_at)
    || !Number.isFinite(Date.parse(signed.created_at)) || !/^[a-f0-9]{64}$/.test(signed.sha256))
    throw new Error('Invalid signed case metadata.');
  const hashes = payload.evidence_hashes;
  if (!Array.isArray(hashes) || hashes.length < 1 || hashes.length > 32
    || hashes.some(hash => typeof hash !== 'string' || !/^[a-f0-9]{64}$/.test(hash))
    || hashes.join(',') !== [...new Set(hashes)].sort().join(','))
    throw new Error('Evidence hashes must be sorted, unique SHA-256 values.');
  const pin = expectedFingerprint.trim().toLowerCase();
  if (pin && !/^[a-f0-9]{64}$/.test(pin)) throw new Error('Expected key fingerprint must be 64 hexadecimal characters.');
  const publicBytes = base64(node.public_key_spki), signature = base64(node.signature);
  const algorithm = { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' };
  let key;
  try { key = await crypto.subtle.importKey('spki', publicBytes, algorithm, false, ['verify']); }
  catch { throw new Error('The receipt public key is not a supported RSA key.'); }
  if (key.algorithm.modulusLength !== 2048 || signature.length !== 256)
    throw new Error('Expected the exporter’s RSA-2048 key and signature.');
  const fingerprint = hex(await crypto.subtle.digest('SHA-256', publicBytes));
  const payloadHash = hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(payload))));
  const signatureValid = await crypto.subtle.verify(algorithm.name, key, signature,
    new TextEncoder().encode(canonical(signed)));
  const hashValid = payloadHash === signed.sha256, keyMatches = pin ? fingerprint === pin : null;
  return { payload, createdAt: signed.created_at, payloadHash, fingerprint, hashValid, signatureValid,
    keyMatches, integrityValid: hashValid && signatureValid, verifiedWithPinnedKey: hashValid && signatureValid && keyMatches === true };
}
