import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import {
  Sprout, ClipboardList, Package, BarChart3, Leaf, Bell,
  Check, ArrowRight, Menu, X,
  Cloud, Shield, Lock, Smartphone, Database, Cpu, Zap, GitBranch,
  Workflow, FileSpreadsheet, QrCode, Wifi, WifiOff, Users, Globe,
  ChevronDown, LineChart, Layers, Server,
} from "lucide-react";
import { useState } from "react";
import { Dialog, DialogContent, DialogTrigger, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { AppDemoPlayer } from "@/components/feature-demos";
import { AppAccessLink } from "@/components/app-access-link";
import logoWhite from "@/assets/brotare-symbol.svg";
import logoGreen from "@/assets/brotare-logo-green.png";
import nursery1 from "@/assets/nursery-1.jpg";
import nursery2 from "@/assets/nursery-2.jpg";
import nursery3 from "@/assets/nursery-3.jpg";
import nursery4 from "@/assets/nursery-4.jpg";

const heroImages = [
  { src: nursery1, alt: "Mudas em produção no viveiro" },
  { src: nursery4, alt: "Estufa com cultivo organizado" },
  { src: nursery3, alt: "Vista aérea do viveiro" },
  { src: nursery2, alt: "Trabalho manual com as mudas" },
];

function HeroSlideshow() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((p) => (p + 1) % heroImages.length), 3800);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="relative aspect-[4/5] w-full max-w-md mx-auto">
      <div className="absolute -inset-4 bg-primary/10 rounded-[2rem] blur-2xl" />
      <div className="relative w-full h-full rounded-[2rem] overflow-hidden shadow-2xl border-4 border-white">
        {heroImages.map((img, idx) => (
          <img
            key={img.src}
            src={img.src}
            alt={img.alt}
            className="absolute inset-0 w-full h-full object-cover transition-opacity duration-[1400ms] ease-in-out"
            style={{ opacity: i === idx ? 1 : 0 }}
          />
        ))}
        <div className="absolute inset-x-0 bottom-0 h-1/4 bg-gradient-to-t from-black/30 to-transparent" />
        <div className="absolute bottom-5 left-1/2 -translate-x-1/2 flex gap-1.5">
          {heroImages.map((_, idx) => (
            <span key={idx} className="h-1 rounded-full transition-all duration-500" style={{ width: i === idx ? 20 : 6, background: i === idx ? "white" : "rgba(255,255,255,0.5)" }} />
          ))}
        </div>
      </div>
      {/* Floating stat badge */}
      <div className="absolute -bottom-6 -left-6 bg-card rounded-2xl shadow-xl border border-border p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <Sprout className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Mudas hoje</p>
          <p className="text-lg font-bold text-deep leading-tight">12.480</p>
        </div>
      </div>
      <div className="absolute -top-5 -right-4 bg-primary text-primary-foreground rounded-2xl shadow-xl px-4 py-3">
        <p className="text-xs opacity-80">Crescimento</p>
        <p className="text-lg font-bold leading-tight">+18%</p>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Brotare — Sistema de Gestão para Viveiros" },
      { name: "description", content: "Brotare é o sistema completo para controle de estoque, produção e vendas do seu viveiro florestal ou ornamental." },
      { property: "og:title", content: "Brotare — Sistema de Gestão para Viveiros" },
      { property: "og:description", content: "Controle de estoque, produção, pedidos e rastreabilidade em uma plataforma feita para viveiros." },
      { property: "og:type", content: "website" },
    ],
    links: [{ rel: "canonical", href: "/" }, { rel: "preconnect", href: "https://fonts.googleapis.com" }, { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" }],
  }),
  component: Index,
});

const features = [
  {
    key: "estoque" as const, Icon: Sprout, title: "Controle de Estoque",
    desc: "Rastreie espécies, quantidades e localização das mudas em tempo real.",
    long: "Saiba exatamente quantas mudas você tem de cada espécie, em qual setor e em qual estágio. O sistema atualiza automaticamente a cada movimentação — entrada, saída, perda ou transferência.",
    bullets: ["Inventário em tempo real por espécie e setor", "Alertas de baixo estoque", "Histórico completo de movimentações", "Códigos e QR Code para cada lote"],
  },
  {
    key: "producao" as const, Icon: ClipboardList, title: "Gestão de Produção",
    desc: "Planeje ciclos de cultivo, irrigação e tratamentos por lote.",
    long: "Organize seus lotes em estágios visuais (semeio, crescimento, aclimatação, pronto) e acompanhe o progresso de cada um com tarefas, irrigação e tratamentos programados.",
    bullets: ["Kanban visual por estágio de cultivo", "Programação de irrigação e adubação", "Registro de tratamentos fitossanitários", "Previsão de data de entrega por lote"],
  },
  {
    key: "pedidos" as const, Icon: Package, title: "Pedidos e Vendas",
    desc: "Gerencie clientes, pedidos e emissão de documentos fiscais.",
    long: "Centralize todos os pedidos em um só lugar, do orçamento à entrega. Cadastre clientes, gere romaneios e emita nota fiscal direto pelo sistema.",
    bullets: ["Catálogo digital com preços por espécie", "Geração automática de romaneios", "Emissão de NF-e integrada", "Histórico de compras por cliente"],
  },
  {
    key: "relatorios" as const, Icon: BarChart3, title: "Relatórios e Análises",
    desc: "Visualize dados de crescimento, perdas e rentabilidade.",
    long: "Tome decisões baseadas em dados reais. Veja gráficos de produção, taxa de sobrevivência, perdas por espécie e rentabilidade por lote.",
    bullets: ["Dashboard com indicadores-chave", "Relatórios de receita e custos", "Análise de perdas por causa", "Exportação em PDF e Excel"],
  },
  {
    key: "rastreabilidade" as const, Icon: Leaf, title: "Rastreabilidade",
    desc: "Histórico completo de cada muda, do semeio à entrega.",
    long: "Toda muda tem uma linha do tempo: quando foi semeada, repicada, tratada e entregue. Essencial para certificações e exigências de órgãos ambientais.",
    bullets: ["Timeline completa por lote", "Origem da semente e fornecedor", "Conformidade com órgãos ambientais", "Relatório de rastreabilidade exportável"],
  },
  {
    key: "alertas" as const, Icon: Bell, title: "Alertas Inteligentes",
    desc: "Notificações automáticas para irrigação, pragas e colheita.",
    long: "O sistema avisa você no momento certo: hora de irrigar um setor, surto de praga em um lote, ou mudas prontas para colheita. Tudo via app, e-mail ou WhatsApp.",
    bullets: ["Notificações por app, e-mail e WhatsApp", "Regras personalizáveis por viveiro", "Alertas climáticos integrados", "Encaminhamento para equipes específicas"],
  },
];

const benefits = [
  "Interface simples, feita para quem trabalha no campo",
  "Acesso pelo celular, tablet ou computador",
  "Dados seguros na nuvem, sem instalação",
  "Suporte em português, com equipe dedicada",
  "Planos acessíveis para viveiros de todos os portes",
];

function useReveal() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const els = ref.current?.querySelectorAll<HTMLElement>(".reveal") ?? [];
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in-view");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  return ref;
}

function BotanicalArt({ className = "", color = "var(--primary)" }: { className?: string; color?: string }) {
  return (
    <svg viewBox="0 0 400 400" className={className} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round">
      <circle cx="200" cy="200" r="160" opacity="0.15" />
      <circle cx="200" cy="200" r="110" opacity="0.2" />
      <g transform="translate(200 200)">
        <path d="M0 -120 Q -10 -60 0 0" strokeWidth="2" />
        <path d="M0 -90 Q -40 -100 -55 -75" />
        <path d="M0 -90 Q 40 -100 55 -75" />
        <path d="M0 -60 Q -50 -65 -70 -35" />
        <path d="M0 -60 Q 50 -65 70 -35" />
        <path d="M0 -30 Q -55 -30 -75 5" />
        <path d="M0 -30 Q 55 -30 75 5" />
        <ellipse cx="-55" cy="-75" rx="22" ry="10" transform="rotate(-30 -55 -75)" fill={color} opacity="0.25" stroke="none" />
        <ellipse cx="55" cy="-75" rx="22" ry="10" transform="rotate(30 55 -75)" fill={color} opacity="0.25" stroke="none" />
        <ellipse cx="-70" cy="-35" rx="26" ry="11" transform="rotate(-20 -70 -35)" fill={color} opacity="0.3" stroke="none" />
        <ellipse cx="70" cy="-35" rx="26" ry="11" transform="rotate(20 70 -35)" fill={color} opacity="0.3" stroke="none" />
        <ellipse cx="-75" cy="5" rx="28" ry="12" transform="rotate(-10 -75 5)" fill={color} opacity="0.35" stroke="none" />
        <ellipse cx="75" cy="5" rx="28" ry="12" transform="rotate(10 75 5)" fill={color} opacity="0.35" stroke="none" />
      </g>
      <circle cx="80" cy="90" r="4" fill={color} opacity="0.4" stroke="none" />
      <circle cx="330" cy="120" r="6" fill={color} opacity="0.3" stroke="none" />
      <circle cx="340" cy="310" r="4" fill={color} opacity="0.4" stroke="none" />
      <circle cx="60" cy="320" r="5" fill={color} opacity="0.3" stroke="none" />
    </svg>
  );
}

function Mockup() {
  return (
    <div className="relative">
      <div className="absolute -inset-6 bg-primary/10 rounded-3xl blur-2xl" />
      <div className="relative bg-card rounded-2xl shadow-2xl border border-border overflow-hidden">
        <div className="flex items-center gap-1.5 px-4 py-3 border-b border-border bg-secondary/50">
          <span className="w-3 h-3 rounded-full bg-primary/30" />
          <span className="w-3 h-3 rounded-full bg-primary/50" />
          <span className="w-3 h-3 rounded-full bg-primary/70" />
          <span className="ml-3 text-xs text-muted-foreground">brotare.app / painel</span>
        </div>
        <div className="p-6 grid grid-cols-3 gap-4">
          {[
            { label: "Mudas ativas", value: "12.480", trend: "+8%" },
            { label: "Lotes em produção", value: "34", trend: "+2" },
            { label: "Pedidos do mês", value: "187", trend: "+24%" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl bg-cream p-4">
              <p className="text-xs text-muted-foreground">{s.label}</p>
              <p className="text-2xl font-bold text-primary mt-1">{s.value}</p>
              <p className="text-xs text-primary-light mt-1">{s.trend}</p>
            </div>
          ))}
        </div>
        <div className="px-6 pb-6">
          <div className="rounded-xl bg-cream p-4 h-40 flex items-end gap-2">
            {[40, 65, 50, 80, 70, 95, 85, 100, 78, 92, 88, 110].map((h, i) => (
              <div key={i} className="flex-1 rounded-t-md bg-gradient-to-t from-primary to-primary-light" style={{ height: `${h}%` }} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Index() {
  const ref = useReveal();
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<string>("top");

  const nav = [
    { href: "#funcionalidades", label: "Funcionalidades" },
    { href: "#fluxo", label: "Fluxo" },
    { href: "#tecnologia", label: "Tecnologia" },
    { href: "#integracoes", label: "Integrações" },
    { href: "#sobre", label: "Sobre" },
    { href: "#faq", label: "FAQ" },
  ];

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (typeof document === "undefined") return;
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  // Track active section via IntersectionObserver
  useEffect(() => {
    if (typeof window === "undefined") return;
    const ids = ["top", ...nav.map((n) => n.href.slice(1))];
    const sections = ids
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => !!el);
    if (!sections.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]?.target.id) setActive(visible[0].target.id);
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: [0, 0.25, 0.5, 1] },
    );
    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className="min-h-screen bg-background text-foreground">
      {/* NAV */}
      <header className="fixed top-0 inset-x-0 z-50 backdrop-blur-md bg-background/80 border-b border-border/60">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href="#top" className="flex items-center" onClick={() => setOpen(false)}>
            <img src={logoGreen} alt="Brotare" className="h-9 w-auto" />
          </a>
          <nav className="hidden md:flex items-center gap-2">
            {nav.map((n) => {
              const id = n.href.slice(1);
              const isActive = active === id;
              return (
                <a
                  key={n.href}
                  href={n.href}
                  className={`relative px-3 py-2 text-sm font-medium transition-colors ${
                    isActive ? "text-primary" : "text-foreground/75 hover:text-primary"
                  }`}
                >
                  {n.label}
                  <span
                    className={`pointer-events-none absolute left-3 right-3 -bottom-0.5 h-0.5 rounded-full bg-primary transition-all duration-300 ${
                      isActive ? "opacity-100 scale-x-100" : "opacity-0 scale-x-0"
                    }`}
                  />
                </a>
              );
            })}
          </nav>
          <AppAccessLink className="hidden md:inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-primary-dark transition-colors">
            Entrar <ArrowRight className="w-4 h-4" />
          </AppAccessLink>
          <button
            className="md:hidden relative w-10 h-10 flex items-center justify-center rounded-full hover:bg-primary/10 transition-colors"
            onClick={() => setOpen((o) => !o)}
            aria-label={open ? "Fechar menu" : "Abrir menu"}
            aria-expanded={open}
          >
            <span className="sr-only">Menu</span>
            <span className="relative w-5 h-4 block">
              <span
                className={`absolute left-0 right-0 h-0.5 bg-deep rounded-full transition-all duration-300 ${
                  open ? "top-1/2 -translate-y-1/2 rotate-45" : "top-0"
                }`}
              />
              <span
                className={`absolute left-0 right-0 top-1/2 -translate-y-1/2 h-0.5 bg-deep rounded-full transition-all duration-200 ${
                  open ? "opacity-0" : "opacity-100"
                }`}
              />
              <span
                className={`absolute left-0 right-0 h-0.5 bg-deep rounded-full transition-all duration-300 ${
                  open ? "top-1/2 -translate-y-1/2 -rotate-45" : "bottom-0"
                }`}
              />
            </span>
          </button>
        </div>

        {/* Mobile menu overlay */}
        <div
          className={`md:hidden fixed inset-x-0 top-16 bottom-0 bg-background/95 backdrop-blur-md transition-all duration-300 ${
            open ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
          }`}
        >
          <div className="px-6 py-8 flex flex-col h-full">
            <nav className="flex-1 flex flex-col gap-1">
              {nav.map((n, i) => {
                const id = n.href.slice(1);
                const isActive = active === id;
                return (
                  <a
                    key={n.href}
                    href={n.href}
                    onClick={() => setOpen(false)}
                    style={{ transitionDelay: open ? `${i * 40}ms` : "0ms" }}
                    className={`flex items-center justify-between py-4 px-4 rounded-xl text-lg font-semibold border transition-all duration-300 ${
                      open ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
                    } ${
                      isActive
                        ? "bg-primary/10 text-primary border-primary/30"
                        : "text-deep border-transparent hover:bg-cream"
                    }`}
                  >
                    {n.label}
                    <ArrowRight className={`w-4 h-4 transition-transform ${isActive ? "translate-x-1" : ""}`} />
                  </a>
                );
              })}
            </nav>
            <AppAccessLink
              onClick={() => setOpen(false)}
              className="mt-6 inline-flex items-center justify-center gap-2 bg-primary text-primary-foreground px-6 py-4 rounded-full text-base font-semibold shadow-lg shadow-primary/20"
            >
              Entrar <ArrowRight className="w-4 h-4" />
            </AppAccessLink>
          </div>
        </div>
      </header>


      {/* HERO */}
      <section id="top" className="relative min-h-screen flex items-center pt-16 overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 -left-32 w-96 h-96 rounded-full bg-primary/10 blur-3xl" />
          <div className="absolute bottom-0 right-0 w-[40rem] h-[40rem] rounded-full bg-primary-light/10 blur-3xl" />
        </div>
        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center py-20">
          <div className="reveal">
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold tracking-wider uppercase">
              <Leaf className="w-3.5 h-3.5" /> Gestão de Viveiros
            </span>
            <h1 className="mt-6 text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.05] text-deep">
              Gerencie seu viveiro com <span className="text-primary">inteligência</span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground max-w-xl leading-relaxed">
              Brotare é o sistema completo para controle de estoque, produção e vendas do seu viveiro florestal ou ornamental.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <AppAccessLink className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-7 py-3.5 rounded-full font-semibold hover:bg-primary-dark transition-colors shadow-lg shadow-primary/20">
                Entrar no painel <ArrowRight className="w-4 h-4" />
              </AppAccessLink>
              <a href="#funcionalidades" className="inline-flex items-center gap-2 border-2 border-primary text-primary px-7 py-3.5 rounded-full font-semibold hover:bg-primary hover:text-primary-foreground transition-colors">
                Saiba mais
              </a>
            </div>
          </div>
          <div className="reveal relative">
            <HeroSlideshow />
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="funcionalidades" className="py-24 md:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto reveal">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Funcionalidades</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
              Tudo que seu viveiro precisa
            </h2>
            <p className="mt-4 text-muted-foreground">
              Uma plataforma feita por especialistas em tecnologia agrícola para o dia a dia real do campo.
            </p>
          </div>
          <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <Dialog key={f.key}>
                <DialogTrigger asChild>
                  <button className="reveal group text-left bg-card rounded-2xl p-7 border border-border hover:border-primary/40 hover:shadow-xl hover:shadow-primary/5 transition-all">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                      <f.Icon className="w-6 h-6" />
                    </div>
                    <h3 className="mt-5 text-lg font-semibold text-deep">{f.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                    <span className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-primary">
                      Ver demo <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </span>
                  </button>
                </DialogTrigger>
                <DialogContent className="max-w-3xl p-0 overflow-hidden bg-background border-border">
                  <div className="grid md:grid-cols-2 max-h-[85vh] overflow-y-auto">
                    <div className="p-7 md:p-8">
                      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                        <f.Icon className="w-6 h-6" />
                      </div>
                      <DialogTitle className="mt-4 text-2xl font-bold tracking-tight text-deep">
                        {f.title}
                      </DialogTitle>
                      <DialogDescription className="mt-3 text-sm leading-relaxed text-muted-foreground">
                        {f.long}
                      </DialogDescription>
                      <ul className="mt-5 space-y-2.5">
                        {f.bullets.map((b) => (
                          <li key={b} className="flex items-start gap-2.5 text-sm text-foreground/90">
                            <span className="mt-1 flex-shrink-0 w-4 h-4 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                              <Check className="w-2.5 h-2.5" strokeWidth={3.5} />
                            </span>
                            {b}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-cream/60 p-6 md:p-7 flex items-center">
                      <div className="w-full">
                        <p className="text-[10px] font-semibold uppercase tracking-widest text-primary mb-3">Demo ao vivo</p>
                        <AppDemoPlayer DemoKey={f.key} />
                      </div>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            ))}
          </div>
        </div>
      </section>

      {/* BENEFITS */}
      <section id="beneficios" className="py-24 md:py-32 bg-cream">
        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
          <div className="reveal">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Benefícios</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
              Por que escolher o Brotare?
            </h2>
            <ul className="mt-8 space-y-4">
              {benefits.map((b) => (
                <li key={b} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center mt-0.5">
                    <Check className="w-3.5 h-3.5" strokeWidth={3} />
                  </span>
                  <span className="text-foreground/90">{b}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="reveal">
            <Mockup />
          </div>
        </div>
      </section>

      {/* WORKFLOW */}
      <section id="fluxo" className="py-24 md:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto reveal">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Fluxo operacional</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
              Do semeio à entrega, em uma única plataforma
            </h2>
            <p className="mt-4 text-muted-foreground">
              O Brotare acompanha cada muda em todas as etapas do ciclo produtivo, com rastreabilidade ponta a ponta e indicadores em tempo real.
            </p>
          </div>
          <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { n: "01", Icon: Sprout, t: "Planejamento e semeio", d: "Defina lotes, calendário agrícola, substratos, sementes e estimativas de germinação. O sistema sugere quantidades com base no histórico." },
              { n: "02", Icon: Workflow, t: "Produção e manejo", d: "Registro de repique, adubação, irrigação, controle fitossanitário e movimentação entre canteiros, estufas e setores." },
              { n: "03", Icon: QrCode, t: "Rastreabilidade por lote", d: "Cada lote recebe um identificador único com QR Code. Toda movimentação é registrada com data, responsável e fotos opcionais." },
              { n: "04", Icon: Package, t: "Venda e expedição", d: "Pedidos, romaneios, notas, separação por carga e baixa automática no estoque ao confirmar a saída." },
            ].map((s) => (
              <div key={s.n} className="reveal relative rounded-2xl border border-border bg-card p-6 hover:border-primary/40 transition-colors">
                <span className="absolute -top-3 left-6 text-xs font-bold tracking-widest text-primary bg-background px-2 py-0.5 rounded-full border border-primary/30">
                  ETAPA {s.n}
                </span>
                <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center text-primary mt-2">
                  <s.Icon className="w-5 h-5" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-deep">{s.t}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* MODULES */}
      <section className="py-24 md:py-32 bg-cream">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto reveal">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Módulos</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
              Uma plataforma modular e completa
            </h2>
            <p className="mt-4 text-muted-foreground">
              Ative apenas o que faz sentido para sua operação. Comece pelo essencial e expanda conforme o viveiro cresce.
            </p>
          </div>
          <div className="mt-14 grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { Icon: Layers, t: "Cadastro técnico", items: ["Catálogo de espécies", "Substratos, recipientes e insumos", "Setores, estufas e canteiros", "Equipe e perfis de acesso"] },
              { Icon: Sprout, t: "Produção", items: ["Plano de cultivo por espécie", "Lotes com ciclo configurável", "Registro de tratos culturais", "Perdas e descarte com motivo"] },
              { Icon: Package, t: "Estoque", items: ["Inventário em tempo real", "Reservas e separação", "Alertas de mínimo e validade", "Movimentações com histórico"] },
              { Icon: ClipboardList, t: "Comercial", items: ["Cadastro de clientes (PF/PJ)", "Orçamentos e pedidos", "Tabela de preços por canal", "Romaneios e notas auxiliares"] },
              { Icon: BarChart3, t: "Indicadores", items: ["Dashboards por área", "Análise de produtividade", "Margem por espécie e cliente", "Exportação CSV / Excel / PDF"] },
              { Icon: Bell, t: "Operação no campo", items: ["App mobile com QR Code", "Modo offline com sincronização", "Notificações de irrigação", "Checklists fitossanitários"] },
            ].map((m) => (
              <div key={m.t} className="reveal rounded-2xl bg-card border border-border p-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <m.Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-semibold text-deep">{m.t}</h3>
                </div>
                <ul className="mt-4 space-y-2">
                  {m.items.map((i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-foreground/85">
                      <Check className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      {i}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TECHNOLOGY */}
      <section id="tecnologia" className="py-24 md:py-32">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-14 items-start">
            <div className="reveal">
              <p className="text-sm font-semibold tracking-widest uppercase text-primary">Tecnologia</p>
              <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
                Arquitetura moderna, pronta para escalar
              </h2>
              <p className="mt-5 text-lg text-muted-foreground leading-relaxed">
                Construído sobre uma stack web atual, com infraestrutura em nuvem, criptografia em trânsito e em repouso, e disponibilidade preparada para operações 24/7.
              </p>
              <div className="mt-8 grid sm:grid-cols-2 gap-4">
                {[
                  { Icon: Cloud, t: "Cloud nativo", d: "Hospedagem em nuvem com escalabilidade automática." },
                  { Icon: Database, t: "PostgreSQL", d: "Banco de dados relacional confiável e auditável." },
                  { Icon: Lock, t: "TLS 1.3 + AES-256", d: "Criptografia ponta a ponta e em repouso." },
                  { Icon: Server, t: "Backups diários", d: "Retenção de 30 dias, restauração ponto a ponto." },
                  { Icon: Cpu, t: "API REST + Webhooks", d: "Integre com ERPs, e-commerce e BI." },
                  { Icon: Smartphone, t: "Mobile-first", d: "Funciona em celular, tablet e desktop." },
                ].map((t) => (
                  <div key={t.t} className="flex gap-3 p-4 rounded-xl border border-border bg-card">
                    <div className="w-9 h-9 flex-shrink-0 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                      <t.Icon className="w-4.5 h-4.5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-deep">{t.t}</p>
                      <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{t.d}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="reveal lg:sticky lg:top-24">
              <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-lg">
                <div className="px-5 py-3 border-b border-border bg-secondary/40 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary" />
                  <p className="text-xs font-semibold uppercase tracking-widest text-deep">Arquitetura em camadas</p>
                </div>
                <div className="p-5 space-y-3">
                  {[
                    { lbl: "Apresentação", v: "Web app (React) · App mobile (PWA)", Icon: Smartphone },
                    { lbl: "API", v: "REST + Webhooks · Rate limit por chave", Icon: GitBranch },
                    { lbl: "Aplicação", v: "Regras de negócio · Multi-tenant", Icon: Cpu },
                    { lbl: "Dados", v: "PostgreSQL · Cache · Object storage", Icon: Database },
                    { lbl: "Infraestrutura", v: "Cloud · Auto-scaling · Observabilidade", Icon: Cloud },
                  ].map((row) => (
                    <div key={row.lbl} className="flex items-center gap-3 p-3 rounded-lg bg-cream">
                      <div className="w-9 h-9 rounded-md bg-primary/15 text-primary flex items-center justify-center">
                        <row.Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">{row.lbl}</p>
                        <p className="text-sm font-medium text-deep truncate">{row.v}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="px-5 py-3 border-t border-border bg-primary/5 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-deep">
                    <Zap className="w-3.5 h-3.5 text-primary" />
                    <span className="font-semibold">SLA 99,9%</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-deep">
                    <Shield className="w-3.5 h-3.5 text-primary" />
                    <span className="font-semibold">LGPD-ready</span>
                  </div>
                </div>
              </div>
              <div className="mt-5 grid grid-cols-3 gap-3">
                {[
                  { Icon: Wifi, t: "Online" },
                  { Icon: WifiOff, t: "Offline" },
                  { Icon: Globe, t: "Multi-unidade" },
                ].map((b) => (
                  <div key={b.t} className="rounded-xl border border-border bg-card p-3 flex items-center gap-2">
                    <b.Icon className="w-4 h-4 text-primary" />
                    <span className="text-xs font-semibold text-deep">{b.t}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* INTEGRATIONS + SECURITY */}
      <section id="integracoes" className="py-24 md:py-32 bg-cream">
        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-12">
          <div className="reveal rounded-2xl bg-card border border-border p-8">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Integrações</p>
            <h3 className="mt-2 text-2xl md:text-3xl font-bold tracking-tight text-deep">
              Conectado ao ecossistema do seu negócio
            </h3>
            <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
              Troque dados com sistemas financeiros, fiscais e operacionais via API REST, webhooks e arquivos padronizados.
            </p>
            <div className="mt-6 grid sm:grid-cols-2 gap-3">
              {[
                { Icon: FileSpreadsheet, t: "Importação CSV / Excel", d: "Migre clientes, espécies e estoque inicial." },
                { Icon: GitBranch, t: "API REST documentada", d: "Endpoints para lotes, pedidos e movimentações." },
                { Icon: Zap, t: "Webhooks de eventos", d: "Receba notificações de pedidos e baixas." },
                { Icon: LineChart, t: "Exportação para BI", d: "Power BI, Looker, Metabase e Google Sheets." },
              ].map((i) => (
                <div key={i.t} className="rounded-xl border border-border bg-background p-4">
                  <div className="w-8 h-8 rounded-md bg-primary/10 text-primary flex items-center justify-center">
                    <i.Icon className="w-4 h-4" />
                  </div>
                  <p className="mt-3 text-sm font-semibold text-deep">{i.t}</p>
                  <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{i.d}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="reveal rounded-2xl bg-card border border-border p-8">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Segurança e conformidade</p>
            <h3 className="mt-2 text-2xl md:text-3xl font-bold tracking-tight text-deep">
              Seus dados protegidos em cada camada
            </h3>
            <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
              Práticas de segurança aplicadas em todo o ciclo de vida da informação, com controles de acesso granulares e auditoria.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                { Icon: Lock, t: "Criptografia AES-256 em repouso e TLS 1.3 em trânsito" },
                { Icon: Users, t: "Perfis de acesso por usuário, setor e operação" },
                { Icon: Shield, t: "Conformidade com a LGPD e termos de consentimento" },
                { Icon: Database, t: "Backups diários automatizados, retenção de 30 dias" },
                { Icon: ClipboardList, t: "Log de auditoria de todas as alterações sensíveis" },
              ].map((s) => (
                <li key={s.t} className="flex items-start gap-3">
                  <span className="w-8 h-8 flex-shrink-0 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                    <s.Icon className="w-4 h-4" />
                  </span>
                  <span className="text-sm text-foreground/90 leading-relaxed pt-1">{s.t}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>



      {/* ABOUT */}
      <section id="sobre" className="py-24 md:py-32">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="reveal">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Sobre</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
              Nascido no campo, feito com tecnologia
            </h2>
            <div className="mt-6 space-y-5 text-lg text-muted-foreground leading-relaxed text-left md:text-center">
              <p>
                A <span className="font-semibold text-deep">Brotare</span> é uma iniciativa de desenvolvimento de uma solução de gestão voltada para viveiros de plantas. Nasce do desejo de apoiar produtores que buscam melhorar a eficiência de seus processos, otimizar a qualidade de seus produtos e ampliar seus resultados financeiros.
              </p>
              <p>
                Desenvolvida para atender às necessidades do setor, a plataforma reúne ferramentas que auxiliam no controle da produção, gestão de estoque, acompanhamento de lotes, organização de vendas e monitoramento de indicadores importantes para a tomada de decisões.
              </p>
              <p>
                Com uma interface intuitiva e foco na realidade dos viveiros brasileiros, a Brotare transforma informações em dados estratégicos, reduzindo desperdícios, aumentando a produtividade e proporcionando mais segurança na gestão do negócio.
              </p>
              <p>
                Mais do que um sistema, a <span className="font-semibold text-deep">Brotare é uma parceira no crescimento sustentável dos viveiros</span>, contribuindo para que produtores tenham mais controle, eficiência e rentabilidade em cada etapa da produção.
              </p>
            </div>
          </div>
          <div className="mt-14 grid grid-cols-3 gap-6 reveal">
            {[
              { v: "500+", l: "viveiros" },
              { v: "12", l: "estados" },
              { v: "99.9%", l: "uptime" },
            ].map((s) => (
              <div key={s.l} className="rounded-2xl border border-border bg-card p-6">
                <p className="text-3xl md:text-4xl font-bold text-primary">{s.v}</p>
                <p className="mt-1 text-sm text-muted-foreground">{s.l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 md:py-32 bg-cream">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center reveal">
            <p className="text-sm font-semibold tracking-widest uppercase text-primary">Perguntas frequentes</p>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-deep">
              Tudo o que você precisa saber
            </h2>
          </div>
          <div className="mt-12 space-y-3 reveal">
            {[
              { q: "O Brotare funciona em qualquer porte de viveiro?", a: "Sim. A plataforma é modular e atende desde pequenos viveiros familiares até operações com múltiplas unidades, dezenas de usuários e centenas de espécies cadastradas." },
              { q: "O Brotare atende viveiros de flores e plantas ornamentais?", a: "Sim. Além de viveiros florestais, frutíferos e nativas, o Brotare atende viveiros de flores, plantas ornamentais e paisagismo. O cadastro de espécies, ciclos de cultivo, recipientes e unidades de venda é totalmente configurável para cada tipo de produção." },
              { q: "Funciona sem internet, no campo?", a: "Sim. O app mobile possui modo offline: você registra plantios, movimentações e leituras de QR Code mesmo sem sinal. Tudo sincroniza automaticamente quando a conexão retorna." },
              { q: "É possível migrar dados de planilhas existentes?", a: "Sim. Disponibilizamos importação por CSV/Excel para clientes, espécies, lotes e estoque inicial, além de suporte da nossa equipe para a estruturação dos dados." },
              { q: "Posso integrar com meu ERP ou sistema fiscal?", a: "Sim. A plataforma expõe API REST documentada e webhooks de eventos. Trabalhamos com integrações para emissão de notas, ERPs do agronegócio e ferramentas de BI." },
              { q: "Como funciona a rastreabilidade por lote?", a: "Cada lote recebe um identificador único e QR Code. Toda movimentação, trato cultural, perda e venda é vinculada ao lote, com data, responsável e localização." },
              { q: "Meus dados estão seguros?", a: "Sim. Utilizamos criptografia em trânsito e em repouso, controle de acesso por perfil, backups diários e práticas alinhadas à LGPD. Você sempre é o titular dos seus dados." },
              { q: "Quanto tempo leva a implantação?", a: "A maioria dos viveiros começa a operar em poucos dias. Oferecemos onboarding guiado, treinamento da equipe e acompanhamento dedicado nos primeiros meses." },
            ].map((item, i) => (
              <details key={i} className="group rounded-xl bg-card border border-border overflow-hidden">
                <summary className="flex items-center justify-between gap-4 p-5 cursor-pointer list-none">
                  <span className="text-base font-semibold text-deep">{item.q}</span>
                  <ChevronDown className="w-5 h-5 text-primary flex-shrink-0 transition-transform group-open:rotate-180" />
                </summary>
                <div className="px-5 pb-5 -mt-1 text-sm text-muted-foreground leading-relaxed">
                  {item.a}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="sistema" className="relative overflow-hidden bg-primary text-primary-foreground">
        <BotanicalArt className="absolute -right-20 -top-20 w-[28rem] opacity-20" color="white" />
        <BotanicalArt className="absolute -left-20 -bottom-20 w-[28rem] opacity-20" color="white" />
        <div className="relative max-w-4xl mx-auto px-6 py-24 md:py-28 text-center">
          <div className="reveal">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight">
              Pronto para transformar a gestão do seu viveiro?
            </h2>
            <div className="mt-10">
              <AppAccessLink className="inline-flex items-center gap-2 bg-white text-primary px-8 py-4 rounded-full font-semibold hover:bg-cream transition-colors shadow-xl">
                Acessar o sistema <ArrowRight className="w-4 h-4" />
              </AppAccessLink>
            </div>
            <p className="mt-5 text-sm text-white/70">Área restrita — use o login fornecido pelo viveiro.</p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer id="contato" className="bg-deep text-white/80">
        <div className="max-w-7xl mx-auto px-6 py-14 flex flex-col md:flex-row md:items-center justify-between gap-8">
          <img src={logoWhite} alt="Brotare" className="h-16 w-auto" />
          <nav className="flex flex-wrap gap-x-8 gap-y-3 text-sm">
            <a href="#" className="hover:text-white transition-colors">Termos de uso</a>
            <a href="#" className="hover:text-white transition-colors">Privacidade</a>
            <a href="#contato" className="hover:text-white transition-colors">Contato</a>
          </nav>
        </div>
        <div className="border-t border-white/10">
          <p className="max-w-7xl mx-auto px-6 py-6 text-xs text-white/50">
            © 2025 Brotare. Todos os direitos reservados.
          </p>
        </div>
      </footer>
    </div>
  );
}
