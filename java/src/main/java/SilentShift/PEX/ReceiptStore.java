package SilentShift.PEX;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.DeserializationFeature;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.security.*;
import java.security.spec.*;
import java.time.Instant;
import java.util.*;

/** Immutable decision receipts. Keys are local operator state, never package assets. */
public final class ReceiptStore {
    private static final ObjectMapper JSON = new ObjectMapper()
        .enable(JsonParser.Feature.STRICT_DUPLICATE_DETECTION)
        .enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS);
    private final Path root;
    private final KeyPair keys;

    public ReceiptStore(Path directory) throws Exception {
        root = directory.toAbsolutePath().normalize();
        Files.createDirectories(root);
        if (Files.isSymbolicLink(root)) throw new IllegalArgumentException("Receipt directory cannot be a symlink");
        Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwx------"));
        // Gateway pool size is one; this OS lock also protects a second JVM.
        try (FileChannel channel = FileChannel.open(root.resolve("keys.lock"),
                StandardOpenOption.CREATE, StandardOpenOption.WRITE);
             FileLock ignored = channel.lock()) {
            Path key = root.resolve("signing-key.pk8");
            KeyFactory factory = KeyFactory.getInstance("RSA");
            if (!Files.exists(key, LinkOption.NOFOLLOW_LINKS)) {
                KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
                generator.initialize(2048);
                KeyPair generated = generator.generateKeyPair();
                publish(key, generated.getPrivate().getEncoded());
            }
            if (Files.isSymbolicLink(key) || Files.size(key) > 4096)
                throw new IllegalArgumentException("Invalid signing key file");
            PrivateKey privateKey = factory.generatePrivate(new PKCS8EncodedKeySpec(Files.readAllBytes(key)));
            java.security.interfaces.RSAPrivateCrtKey rsa = (java.security.interfaces.RSAPrivateCrtKey) privateKey;
            PublicKey publicKey = factory.generatePublic(new RSAPublicKeySpec(rsa.getModulus(), rsa.getPublicExponent()));
            keys = new KeyPair(publicKey, privateKey);
        }
    }

    public static String sha256(byte[] bytes) throws Exception {
        StringBuilder hex = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(bytes)) hex.append(String.format("%02x", b & 255));
        return hex.toString();
    }

    /** Only these explicit fields enter the fingerprint; timestamps do not defeat idempotency. */
    private static SortedMap<String, Object> payload(String input) throws Exception {
        if (input == null || input.length() > 32768) throw new IllegalArgumentException("Receipt input exceeds bound");
        JsonNode source = JSON.readTree(input);
        if (!source.isObject() || source.size() != 5) throw new IllegalArgumentException("Unexpected receipt fields");
        String id = source.path("case_id").asText("");
        String decision = source.path("decision").asText("");
        String mode = source.path("execution_mode").asText("");
        if (!id.matches("[A-Za-z0-9_-]{1,80}")) throw new IllegalArgumentException("Invalid case id");
        if (!Arrays.asList("DELIVERED", "QUARANTINED", "REVIEW", "REJECTED").contains(decision))
            throw new IllegalArgumentException("Receipt requires a persisted routing outcome");
        if (!Arrays.asList("live", "recorded-replay").contains(mode) || !source.path("synthetic").isBoolean()) throw new IllegalArgumentException("Invalid evaluation metadata");
        JsonNode hashes = source.path("evidence_hashes");
        if (!hashes.isArray() || hashes.size() < 1 || hashes.size() > 32) throw new IllegalArgumentException("Invalid evidence count");
        SortedSet<String> sorted = new TreeSet<>();
        for (JsonNode hash : hashes) {
            if (!hash.isTextual() || !hash.textValue().matches("[a-f0-9]{64}")) throw new IllegalArgumentException("Invalid evidence hash");
            sorted.add(hash.textValue());
        }
        SortedMap<String, Object> result = new TreeMap<>();
        result.put("case_id", id); result.put("decision", decision); result.put("evidence_hashes", sorted);
        result.put("execution_mode", mode); result.put("synthetic", source.path("synthetic").booleanValue());
        return result;
    }

    public synchronized String export(String input) throws Exception {
        SortedMap<String, Object> payload = payload(input);
        byte[] canonical = JSON.writeValueAsBytes(payload);
        String hash = sha256(canonical);
        Path target = root.resolve(payload.get("case_id") + "-" + hash + ".json");
        SortedMap<String, Object> signed = new TreeMap<>();
        signed.put("payload", payload); signed.put("sha256", hash);
        signed.put("schema", "silentshift-java-pex/1"); signed.put("created_at", Instant.now().toString());
        byte[] signedBytes = JSON.writeValueAsBytes(signed);
        Signature signer = Signature.getInstance("SHA256withRSA");
        signer.initSign(keys.getPrivate()); signer.update(signedBytes);
        SortedMap<String, Object> receipt = new TreeMap<>();
        receipt.put("signed", signed); receipt.put("signature_algorithm", "SHA256withRSA");
        receipt.put("signature", Base64.getEncoder().encodeToString(signer.sign()));
        receipt.put("public_key_spki", Base64.getEncoder().encodeToString(keys.getPublic().getEncoded()));
        try { publish(target, JSON.writeValueAsBytes(receipt)); }
        catch (FileAlreadyExistsException duplicate) { /* verify the immutable original below */ }
        if (Files.isSymbolicLink(target) || Files.size(target) > 65536) throw new IllegalStateException("Invalid existing receipt");
        String original = Files.readString(target, StandardCharsets.UTF_8);
        if (!verify(original) || !JSON.readTree(original).path("signed").path("sha256").asText().equals(hash)
                || !JSON.readTree(original).path("public_key_spki").asText().equals(receipt.get("public_key_spki")))
            throw new IllegalStateException("Existing receipt does not match signing identity and outcome");
        return original;
    }

    private static void publish(Path target, byte[] bytes) throws Exception {
        Path temporary = Files.createTempFile(target.getParent(), ".receipt-", ".tmp",
            PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
        try {
            Files.write(temporary, bytes, StandardOpenOption.TRUNCATE_EXISTING);
            try (FileChannel channel = FileChannel.open(temporary, StandardOpenOption.WRITE)) { channel.force(true); }
            // A hard link publishes a complete file atomically and refuses replacement.
            Files.createLink(target, temporary);
        } finally { Files.deleteIfExists(temporary); }
    }

    public static boolean verify(String receipt) {
        try {
            JsonNode node = JSON.readTree(receipt), signed = node.path("signed");
            if (!node.path("signature_algorithm").asText().equals("SHA256withRSA")
                || !signed.path("schema").asText().equals("silentshift-java-pex/1")) return false;
            SortedMap<String, Object> payload = payload(JSON.writeValueAsString(signed.path("payload")));
            if (!sha256(JSON.writeValueAsBytes(payload)).equals(signed.path("sha256").asText())) return false;
            // Sort all signed map keys, including the nested payload, exactly as on export.
            SortedMap<String, Object> canonical = new TreeMap<>();
            canonical.put("created_at", signed.path("created_at").asText()); canonical.put("payload", payload);
            canonical.put("schema", signed.path("schema").asText()); canonical.put("sha256", signed.path("sha256").asText());
            PublicKey key = KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(
                Base64.getDecoder().decode(node.path("public_key_spki").asText())));
            Signature verifier = Signature.getInstance("SHA256withRSA"); verifier.initVerify(key);
            verifier.update(JSON.writeValueAsBytes(canonical));
            return verifier.verify(Base64.getDecoder().decode(node.path("signature").asText()));
        } catch (Exception invalid) { return false; }
    }
}
