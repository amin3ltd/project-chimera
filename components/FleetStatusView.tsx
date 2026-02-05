import React from 'react';

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, Progress } from './ui';

export type AgentState = 'planning' | 'working' | 'judging' | 'sleeping' | 'offline';

export type FleetAgent = {
  agent_id: string;
  display_name: string;
  niche?: string;
  state: AgentState;
  wallet_usdc: number;
  wallet_eth: number;
  hitl_queue_depth: number;
  last_seen: string; // ISO-ish
};

function stateBadge(state: AgentState): { label: string; className: string } {
  switch (state) {
    case 'planning':
      return { label: 'Planning', className: 'bg-indigo-600 text-white' };
    case 'working':
      return { label: 'Working', className: 'bg-sky-600 text-white' };
    case 'judging':
      return { label: 'Judging', className: 'bg-amber-500 text-white' };
    case 'sleeping':
      return { label: 'Sleeping', className: 'bg-slate-700 text-white' };
    case 'offline':
    default:
      return { label: 'Offline', className: 'bg-slate-400 text-white' };
  }
}

function healthFromBalances(usdc: number, eth: number): { label: string; pct: number; bar: string } {
  // Simple heuristic; real implementation would incorporate spend/budget + gas.
  const score = Math.max(0, Math.min(100, Math.round(usdc * 1.5 + eth * 20)));
  if (score >= 70) return { label: 'Healthy', pct: score, bar: 'bg-emerald-500' };
  if (score >= 35) return { label: 'Watch', pct: score, bar: 'bg-amber-500' };
  return { label: 'Low funds', pct: score, bar: 'bg-rose-600' };
}

const demoFleet: FleetAgent[] = [
  {
    agent_id: 'chimera-001',
    display_name: 'Chimera One',
    niche: 'AI / Tech',
    state: 'working',
    wallet_usdc: 32.4,
    wallet_eth: 0.08,
    hitl_queue_depth: 2,
    last_seen: '2026-02-05T08:33:00Z',
  },
  {
    agent_id: 'chimera-002',
    display_name: 'Chimera Two',
    niche: 'Startup / Founder',
    state: 'planning',
    wallet_usdc: 12.0,
    wallet_eth: 0.02,
    hitl_queue_depth: 6,
    last_seen: '2026-02-05T08:31:12Z',
  },
  {
    agent_id: 'chimera-003',
    display_name: 'Chimera Three',
    niche: 'Design / Visual',
    state: 'sleeping',
    wallet_usdc: 4.2,
    wallet_eth: 0.01,
    hitl_queue_depth: 0,
    last_seen: '2026-02-05T07:55:40Z',
  },
  {
    agent_id: 'chimera-004',
    display_name: 'Chimera Four',
    niche: 'Commerce / Deals',
    state: 'judging',
    wallet_usdc: 58.9,
    wallet_eth: 0.14,
    hitl_queue_depth: 1,
    last_seen: '2026-02-05T08:32:25Z',
  },
];

export function FleetStatusView(props: {
  agents?: FleetAgent[];
  onRefresh?: () => void;
}) {
  const agents = props.agents ?? demoFleet;

  const totalHitl = agents.reduce((acc, a) => acc + a.hitl_queue_depth, 0);
  const offline = agents.filter((a) => a.state === 'offline').length;

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900">
            Fleet Status
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Live view of agent state, wallet health, and HITL load.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className="bg-white">
            Agents: {agents.length}
          </Badge>
          <Badge variant="outline" className="bg-white">
            HITL queue: {totalHitl}
          </Badge>
          <Badge
            className={offline > 0 ? 'bg-rose-600 text-white' : 'bg-emerald-600 text-white'}
          >
            Offline: {offline}
          </Badge>
          <Button variant="outline" onClick={props.onRefresh}>
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        {agents.map((agent) => {
          const sb = stateBadge(agent.state);
          const hf = healthFromBalances(agent.wallet_usdc, agent.wallet_eth);

          return (
            <Card key={agent.agent_id} className="border-slate-200">
              <CardHeader className="gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <CardTitle className="text-base">{agent.display_name}</CardTitle>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span className="truncate">{agent.agent_id}</span>
                    {agent.niche ? (
                      <Badge variant="outline" className="bg-white">
                        {agent.niche}
                      </Badge>
                    ) : null}
                    <span className="hidden sm:inline">•</span>
                    <span className="truncate">Last seen: {agent.last_seen}</span>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className={sb.className}>{sb.label}</Badge>
                  <Badge
                    className={
                      agent.hitl_queue_depth > 3
                        ? 'bg-rose-600 text-white'
                        : 'bg-slate-900 text-white'
                    }
                  >
                    HITL: {agent.hitl_queue_depth}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                  <div className="rounded-xl border border-slate-200 bg-white p-3">
                    <div className="text-xs text-slate-500">USDC</div>
                    <div className="mt-1 text-lg font-bold text-slate-900">
                      {agent.wallet_usdc.toFixed(2)}
                    </div>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-white p-3">
                    <div className="text-xs text-slate-500">ETH</div>
                    <div className="mt-1 text-lg font-bold text-slate-900">
                      {agent.wallet_eth.toFixed(3)}
                    </div>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-white p-3">
                    <div className="text-xs text-slate-500">Wallet health</div>
                    <div className="mt-1 flex items-center justify-between gap-2">
                      <span className="text-sm font-semibold text-slate-900">{hf.label}</span>
                      <span className="text-xs text-slate-500">{hf.pct}%</span>
                    </div>
                    <Progress value={hf.pct} className="mt-2" />
                  </div>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="text-xs text-slate-500">
                    SRS alignment: state + balances + HITL depth.
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button size="sm" variant="outline">
                      View logs
                    </Button>
                    <Button size="sm">
                      Open agent
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

export default FleetStatusView;

