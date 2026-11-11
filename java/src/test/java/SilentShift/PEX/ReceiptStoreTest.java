package SilentShift.PEX;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

class ReceiptStoreTest {
    @TempDir Path directory;
    private static String payload(String decision) {
        return "{\"case_id\":\"synthetic-01\",\"decision\":\""+decision+"\",\"evidence_hashes\":[\""+"a".repeat(64)+"\"],\"execution_mode\":\"recorded-replay\",\"synthetic\":true}";
    }
    @Test void standardHashVector() throws Exception {
        assertEquals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", ReceiptStore.sha256("abc".getBytes(StandardCharsets.UTF_8)));
    }
    @Test void signedReceiptRejectsTampering() throws Exception {
        String receipt = new ReceiptStore(directory).export(payload("QUARANTINED"));
        assertTrue(ReceiptStore.verify(receipt));
        assertFalse(ReceiptStore.verify(receipt.replace("QUARANTINED", "DELIVERED")));
        assertFalse(ReceiptStore.verify(receipt.replace("created_at", "tampered_at")));
    }
    @Test void retryAndRestartReuseOriginal() throws Exception {
        ReceiptStore store = new ReceiptStore(directory);
        String first = store.export(payload("DELIVERED"));
        assertEquals(first, store.export(payload("DELIVERED")));
        assertEquals(first, new ReceiptStore(directory).export(payload("DELIVERED")));
        try (java.util.stream.Stream<Path> files = Files.list(directory)) {
            assertEquals(1L, files.filter(p -> p.toString().endsWith(".json")).count());
        }
    }
    @Test void laterDecisionAppendsWithoutOverwriting() throws Exception {
        ReceiptStore store = new ReceiptStore(directory);
        String held = store.export(payload("REVIEW"));
        assertNotEquals(held, store.export(payload("REJECTED")));
        assertEquals(held, store.export(payload("REVIEW")));
    }
    @Test void inputBoundsAndTraversal() throws Exception {
        ReceiptStore store = new ReceiptStore(directory);
        assertThrows(Exception.class, () -> store.export(payload("DELIVERED").replace("synthetic-01", "../escape")));
        assertThrows(Exception.class, () -> store.export(payload("ALLOW")));
        assertThrows(Exception.class, () -> store.export(payload("DELIVERED").replace("a".repeat(64), "bad")));
        assertThrows(Exception.class, () -> store.export(payload("DELIVERED")+" {}"));
        assertThrows(Exception.class, () -> store.export("x".repeat(32769)));
        assertThrows(Exception.class, () -> store.export(payload("DELIVERED").replace("\"synthetic\":true", "\"synthetic\":true,\"synthetic\":true")));
    }
    @Test void concurrentRetriesPublishOnce() throws Exception {
        ReceiptStore store = new ReceiptStore(directory);
        ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            java.util.List<Future<String>> results = new java.util.ArrayList<>();
            for (int i=0; i<8; i++) results.add(pool.submit(() -> store.export(payload("DELIVERED"))));
            String first = results.get(0).get();
            for (Future<String> result : results) assertEquals(first, result.get());
        } finally { pool.shutdownNow(); }
    }
    @Test void corruptedExistingRecordIsNeverReplaced() throws Exception {
        ReceiptStore store = new ReceiptStore(directory);
        store.export(payload("QUARANTINED"));
        Path receipt;
        try (java.util.stream.Stream<Path> files = Files.list(directory)) {
            receipt = files.filter(p -> p.toString().endsWith(".json")).findFirst().orElseThrow();
        }
        Files.writeString(receipt, "corrupted");
        assertThrows(Exception.class, () -> store.export(payload("QUARANTINED")));
        assertEquals("corrupted", Files.readString(receipt));
    }
}
