package SilentShift.PEX;

import com.intersystems.enslib.pex.BusinessOperation;
import com.intersystems.jdbc.IRISObject;
import java.nio.file.Paths;

/** Invoked by the native Destination/Quarantine operations after their route commits. */
public final class ReceiptExporter extends BusinessOperation {
    public String Directory = "";
    private ReceiptStore store;

    @Override public void OnInit() throws Exception {
        if (Directory.isEmpty()) throw new IllegalArgumentException("ReceiptExporter Directory is required");
        store = new ReceiptStore(Paths.get(Directory));
    }

    @Override public void OnTearDown() { }

    @Override public Object OnMessage(Object request) throws Exception {
        if (!(request instanceof IRISObject)) throw new IllegalArgumentException("Native export request required");
        IRISObject message = (IRISObject) request;
        String receipt = store.export(message.getString("PayloadJSON"));
        IRISObject response = (IRISObject) message.iris.classMethodObject("SilentShift.PEX.ExportResponse", "%New");
        response.set("ReceiptJSON", receipt);
        response.set("SignatureValid", ReceiptStore.verify(receipt));
        return response;
    }
}
