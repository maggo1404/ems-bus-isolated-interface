"""Shared helpers: read a tscircuit circuit.json and build the connectivity (nets) from source_traces."""
import json, collections


def load(path="dist/index/circuit.json"):
    return json.load(open(path))


class Conn:
    def __init__(self, cj):
        self.cj = cj
        self.comp = {c["source_component_id"]: c["name"] for c in cj if c["type"] == "source_component"}
        self.ports = {}  # source_port_id -> (ref, pin_number)
        for p in cj:
            if p["type"] == "source_port" and p.get("pin_number") is not None:
                self.ports[p["source_port_id"]] = (self.comp.get(p.get("source_component_id"), "?"), p["pin_number"])
        self.nets = {n["source_net_id"]: n["name"] for n in cj if n["type"] == "source_net"}
        self.par = {}
        for t in cj:
            if t["type"] == "source_trace":
                ids = list(t.get("connected_source_port_ids", [])) + list(t.get("connected_source_net_ids", []))
                for i in ids:
                    self._find(i)
                for i in ids[1:]:
                    self.par[self._find(i)] = self._find(ids[0])
                if "source_trace_id" in t:
                    pass
        # trace id -> root
        self.trace_root = {}
        for t in cj:
            if t["type"] == "source_trace":
                ids = list(t.get("connected_source_port_ids", [])) + list(t.get("connected_source_net_ids", []))
                if ids:
                    self.trace_root[t["source_trace_id"]] = self._find(ids[0])
        groups = collections.defaultdict(lambda: {"pins": set(), "names": set()})
        for k in list(self.par):
            g = self._find(k)
            if k in self.ports:
                groups[g]["pins"].add("%s.%s" % self.ports[k])
            elif k in self.nets:
                groups[g]["names"].add(self.nets[k])
        self.groups = dict(groups)

    def _find(self, x):
        self.par.setdefault(x, x)
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]
            x = self.par[x]
        return x

    def root_of_port(self, source_port_id):
        return self._find(source_port_id) if source_port_id in self.par else None

    def root_of_net(self, source_net_id):
        return self._find(source_net_id) if source_net_id in self.par else None
