import * as React from "react";
import { Sprout, ClipboardList, Package, BarChart3, Leaf, Bell, ArrowUpRight, Droplets, AlertTriangle, TrendingUp } from "lucide-react";

type DemoProps = { frame: number };

// Demo 1: Estoque — list of species with live count ticking
function StockDemo({ frame }: DemoProps) {
  const rows = [
    { name: "Ipê-amarelo", code: "IPA-021", base: 2480, color: "bg-yellow-400" },
    { name: "Aroeira", code: "ARO-103", base: 1820, color: "bg-primary" },
    { name: "Pau-brasil", code: "PBR-007", base: 940, color: "bg-orange-500" },
    { name: "Jacarandá", code: "JAC-055", base: 1320, color: "bg-primary-light" },
  ];
  return (
    <div className="p-5 space-y-2">
      {rows.map((r, i) => {
        const v = r.base + Math.floor(Math.sin((frame + i * 12) / 18) * 6 + 6);
        const pct = 30 + ((frame + i * 25) % 70);
        const active = Math.floor(frame / 30) % rows.length === i;
        return (
          <div key={r.code} className={`rounded-lg border bg-card p-3 flex items-center gap-3 transition-all ${active ? "border-primary shadow-md" : "border-border"}`}>
            <div className={`w-9 h-9 rounded-md ${r.color}/20 flex items-center justify-center`}>
              <Leaf className={`w-4 h-4 text-deep`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-deep truncate">{r.name}</p>
                <p className="text-sm font-bold text-primary tabular-nums">{v.toLocaleString("pt-BR")}</p>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-[10px] text-muted-foreground">{r.code}</p>
                <div className="flex-1 h-1 rounded-full bg-cream overflow-hidden">
                  <div className={`h-full ${r.color}`} style={{ width: `${pct}%`, transition: "width 800ms ease" }} />
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Demo 2: Produção — kanban-style lots moving through stages
function ProductionDemo({ frame }: DemoProps) {
  const stages = ["Semeio", "Crescimento", "Aclimatação", "Pronto"];
  const lots = [
    { id: "L-12", name: "Aroeira" },
    { id: "L-13", name: "Ipê" },
    { id: "L-14", name: "Jacarandá" },
    { id: "L-15", name: "Pau-Brasil" },
  ];
  return (
    <div className="p-4 grid grid-cols-4 gap-2 h-full">
      {stages.map((s, si) => (
        <div key={s} className="rounded-lg bg-cream p-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-2">{s}</p>
          <div className="space-y-1.5">
            {lots.map((l, li) => {
              const pos = (li + Math.floor(frame / 45)) % 4;
              if (pos !== si) return null;
              return (
                <div key={l.id} className="rounded-md bg-card border border-border p-2 shadow-sm">
                  <p className="text-[10px] text-muted-foreground">{l.id}</p>
                  <p className="text-xs font-semibold text-deep">{l.name}</p>
                  <div className="mt-1 h-1 rounded-full bg-cream overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${25 + si * 25}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

// Demo 3: Pedidos — incoming orders animating in
function OrdersDemo({ frame }: DemoProps) {
  const orders = [
    { c: "Fazenda São João", q: 1200, v: "R$ 8.400" },
    { c: "Reflorestar Ltda", q: 800, v: "R$ 5.600" },
    { c: "Prefeitura Verde", q: 2500, v: "R$ 17.500" },
    { c: "Sítio Boa Vista", q: 350, v: "R$ 2.450" },
  ];
  const visible = Math.min(orders.length, 1 + Math.floor(frame / 40));
  return (
    <div className="p-5 space-y-2">
      {orders.slice(0, visible).map((o, i) => (
        <div key={o.c} className="rounded-lg border border-border bg-card p-3 flex items-center gap-3 animate-in fade-in slide-in-from-bottom-2 duration-500">
          <div className="w-9 h-9 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">
            {o.c.split(" ").map((w) => w[0]).slice(0, 2).join("")}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-deep truncate">{o.c}</p>
            <p className="text-[11px] text-muted-foreground">{o.q.toLocaleString("pt-BR")} mudas</p>
          </div>
          <p className="text-sm font-bold text-primary">{o.v}</p>
        </div>
      ))}
      {visible >= orders.length && (
        <div className="rounded-lg bg-primary/10 text-primary text-xs font-semibold p-2 text-center">
          Total: R$ 33.950 · 4 pedidos
        </div>
      )}
    </div>
  );
}

// Demo 4: Relatórios — animated bar chart
function ReportsDemo({ frame }: DemoProps) {
  const months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul"];
  const data = months.map((_, i) => 40 + Math.sin((frame + i * 30) / 25) * 20 + i * 8);
  return (
    <div className="p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Receita</p>
          <p className="text-xl font-bold text-deep">R$ 184.230</p>
        </div>
        <div className="flex items-center gap-1 text-primary text-xs font-semibold bg-primary/10 px-2 py-1 rounded-md">
          <TrendingUp className="w-3 h-3" /> +24%
        </div>
      </div>
      <div className="h-32 flex items-end gap-2">
        {data.map((h, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <div className="w-full rounded-t-md bg-gradient-to-t from-primary to-primary-light" style={{ height: `${h}%`, transition: "height 600ms ease" }} />
            <span className="text-[9px] text-muted-foreground">{months[i]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Demo 5: Rastreabilidade — timeline
function TraceDemo({ frame }: DemoProps) {
  const steps = [
    { t: "Semeio", d: "12/03/2025" },
    { t: "Germinação", d: "28/03/2025" },
    { t: "Repique", d: "15/04/2025" },
    { t: "Aclimatação", d: "10/05/2025" },
    { t: "Entrega", d: "28/05/2025" },
  ];
  const active = Math.min(steps.length - 1, Math.floor(frame / 25));
  return (
    <div className="p-5">
      <div className="bg-cream rounded-lg p-3 mb-3">
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Muda</p>
        <p className="text-sm font-bold text-deep">IPA-021 · Ipê-amarelo</p>
      </div>
      <div className="relative pl-6">
        <div className="absolute left-[7px] top-1 bottom-1 w-0.5 bg-border" />
        <div className="absolute left-[7px] top-1 w-0.5 bg-primary" style={{ height: `${(active / (steps.length - 1)) * 100}%`, transition: "height 500ms ease" }} />
        {steps.map((s, i) => (
          <div key={s.t} className="relative pb-3 last:pb-0">
            <span className={`absolute -left-[22px] top-0.5 w-3.5 h-3.5 rounded-full border-2 ${i <= active ? "bg-primary border-primary" : "bg-card border-border"}`} />
            <p className={`text-sm font-semibold ${i <= active ? "text-deep" : "text-muted-foreground"}`}>{s.t}</p>
            <p className="text-[10px] text-muted-foreground">{s.d}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// Demo 6: Alertas — notifications popping in
function AlertsDemo({ frame }: DemoProps) {
  const alerts = [
    { Icon: Droplets, t: "Irrigação programada", d: "Setor B · em 15 min", c: "text-blue-600 bg-blue-50" },
    { Icon: AlertTriangle, t: "Praga detectada", d: "Lote L-12 · Aroeira", c: "text-orange-600 bg-orange-50" },
    { Icon: Sprout, t: "Pronto para colheita", d: "120 mudas · Ipê", c: "text-primary bg-primary/10" },
  ];
  const visible = Math.min(alerts.length, 1 + Math.floor(frame / 40));
  return (
    <div className="p-5 space-y-2">
      {alerts.slice(0, visible).map(({ Icon, t, d, c }) => (
        <div key={t} className="rounded-lg border border-border bg-card p-3 flex items-start gap-3 animate-in fade-in slide-in-from-right-2 duration-500">
          <div className={`w-9 h-9 rounded-lg ${c} flex items-center justify-center flex-shrink-0`}>
            <Icon className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-deep">{t}</p>
            <p className="text-[11px] text-muted-foreground">{d}</p>
          </div>
          <ArrowUpRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
        </div>
      ))}
    </div>
  );
}

export const featureDemos: Record<string, React.FC<DemoProps>> = {
  estoque: StockDemo,
  producao: ProductionDemo,
  pedidos: OrdersDemo,
  relatorios: ReportsDemo,
  rastreabilidade: TraceDemo,
  alertas: AlertsDemo,
};

// Animated "app" frame around a demo
export function AppDemoPlayer({ DemoKey }: { DemoKey: keyof typeof featureDemos }) {
  const [frame, setFrame] = React.useState(0);
  React.useEffect(() => {
    let raf = 0;
    let last = performance.now();
    const tick = (t: number) => {
      if (t - last > 1000 / 30) {
        setFrame((f) => f + 1);
        last = t;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);
  const Demo = featureDemos[DemoKey];
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden shadow-lg">
      <div className="flex items-center gap-1.5 px-3 py-2 border-b border-border bg-secondary/50">
        <span className="w-2.5 h-2.5 rounded-full bg-primary/30" />
        <span className="w-2.5 h-2.5 rounded-full bg-primary/50" />
        <span className="w-2.5 h-2.5 rounded-full bg-primary/70" />
        <span className="ml-2 text-[10px] text-muted-foreground">brotare.app</span>
        <span className="ml-auto flex items-center gap-1 text-[10px] text-primary font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" /> demo
        </span>
      </div>
      <div className="bg-cream/40 min-h-[260px]">
        <Demo frame={frame} />
      </div>
    </div>
  );
}
