Class SilentShift.Production Extends Ens.Production
{
XData ProductionDefinition
{
<Production Name="SilentShift.Production" TestingEnabled="true" LogGeneralTraceEvents="false">
  <Description>Semantic integrity with native AI Hub proposals and deterministic delivery gates.</Description>
  <ActorPoolSize>2</ActorPoolSize>
  <Item Name="Partner" Category="Ingress" ClassName="SilentShift.Service.Partner" PoolSize="0" Enabled="true" Foreground="false" Comment="Authenticated push service" LogTraceEvents="false" Schedule="" />
  <Item Name="Semantic" Category="Orchestration" ClassName="SilentShift.Process.Semantic" PoolSize="2" Enabled="true" Foreground="false" Comment="Own pool; bounded synchronous calls only to operations" LogTraceEvents="false" Schedule="" />
  <Item Name="References" Category="Evidence" ClassName="SilentShift.Operation.References" PoolSize="1" Enabled="true" Foreground="false" Comment="Independent reference snapshots" LogTraceEvents="false" Schedule="" />
  <Item Name="Investigator" Category="Native AI Hub" ClassName="SilentShift.Operation.Investigation" PoolSize="1" Enabled="true" Foreground="false" Comment="Read-only bounded native investigation" LogTraceEvents="false" Schedule="" />
  <Item Name="Destination" Category="Routing" ClassName="SilentShift.Operation.Destination" PoolSize="1" Enabled="true" Foreground="false" Comment="Idempotent IRIS simulator; rechecks policy" LogTraceEvents="false" Schedule="" />
  <Item Name="Quarantine" Category="Routing" ClassName="SilentShift.Operation.Quarantine" PoolSize="1" Enabled="true" Foreground="false" Comment="Held messages cannot reach destination" LogTraceEvents="false" Schedule="" />
</Production>
}
}
