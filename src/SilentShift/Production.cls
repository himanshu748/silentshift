Class SilentShift.Production Extends Ens.Production
{
XData ProductionDefinition
{
<Production Name="SilentShift.Production" TestingEnabled="true" LogGeneralTraceEvents="false">
  <Description>Semantic integrity with native AI Hub proposals and deterministic delivery gates.</Description>
  <ActorPoolSize>2</ActorPoolSize>
  <Item Name="Partner" Category="Ingress" ClassName="SilentShift.Service.Partner" PoolSize="0" Enabled="true" Foreground="false" Comment="Authenticated push service" LogTraceEvents="false" Schedule="" />
  <Item Name="PartnerFiles" Category="Ingress" ClassName="SilentShift.Service.PartnerFiles" PoolSize="1" Enabled="true" Foreground="false" Comment="Opt-in bounded ready-file adapter" LogTraceEvents="false" Schedule="">
    <Setting Target="Adapter" Name="CallInterval">1</Setting>
    <Setting Target="Adapter" Name="BatchLimit">4</Setting>
    <Setting Target="Adapter" Name="MaxBytes">131072</Setting>
    <Setting Target="Adapter" Name="MaxRetries">3</Setting>
  </Item>
  <Item Name="Semantic" Category="Orchestration" ClassName="SilentShift.Process.Semantic" PoolSize="2" Enabled="true" Foreground="false" Comment="Own pool; bounded synchronous calls only to operations" LogTraceEvents="false" Schedule="" />
  <Item Name="References" Category="Evidence" ClassName="SilentShift.Operation.References" PoolSize="1" Enabled="true" Foreground="false" Comment="Independent reference snapshots" LogTraceEvents="false" Schedule="" />
  <Item Name="Runbooks" Category="Investigation context" ClassName="SilentShift.Operation.Runbooks" PoolSize="1" Enabled="true" Foreground="false" Comment="Local embeddings and IRIS vector procedure retrieval; no release authority" LogTraceEvents="false" Schedule="" />
  <Item Name="Investigator" Category="Native AI Hub" ClassName="SilentShift.Operation.Investigation" PoolSize="1" Enabled="true" Foreground="false" Comment="Read-only bounded native investigation" LogTraceEvents="false" Schedule="" />
  <Item Name="ProviderIngress" Category="Provider trace" ClassName="SilentShift.Provider.Ingress" PoolSize="0" Enabled="true" Foreground="false" Comment="Bearer-bound SDK transport; original case session" LogTraceEvents="false" Schedule="" />
  <Item Name="ProviderForwarder" Category="Provider trace" ClassName="SilentShift.Provider.Forwarder" PoolSize="1" Enabled="true" Foreground="false" Comment="Actual local Ollama calls and paired native responses; own pool" LogTraceEvents="false" Schedule="" />
  <Item Name="AITrace" Category="Observability" ClassName="SilentShift.Operation.AITrace" PoolSize="1" Enabled="true" Foreground="false" Comment="Typed agent-invocation and tool spans; no routing authority" LogTraceEvents="false" Schedule="" />
  <Item Name="ReviewCoordinator" Category="Human review" ClassName="SilentShift.Workflow.Coordinator" PoolSize="1" Enabled="true" Foreground="false" Comment="Durable native reviewer task lifecycle" LogTraceEvents="false" Schedule="" />
  <Item Name="ReviewWorklist" Category="Human review" ClassName="EnsLib.Workflow.Operation" PoolSize="1" Enabled="true" Foreground="false" Comment="Native Workflow Engine task distribution" LogTraceEvents="false" Schedule="" />
  <Item Name="Destination" Category="Routing" ClassName="SilentShift.Operation.Destination" PoolSize="1" Enabled="true" Foreground="false" Comment="Idempotent IRIS simulator; rechecks policy" LogTraceEvents="false" Schedule="" />
  <Item Name="Quarantine" Category="Routing" ClassName="SilentShift.Operation.Quarantine" PoolSize="1" Enabled="true" Foreground="false" Comment="Held messages cannot reach destination" LogTraceEvents="false" Schedule="" />
</Production>
}
}
