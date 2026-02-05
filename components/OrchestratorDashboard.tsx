import React, { useState } from 'react';

import { CampaignComposer } from './CampaignComposer';
import { FleetStatusView } from './FleetStatusView';
import { Dashboard as HitlDashboard } from './Dashboard';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from './ui';

type TabKey = 'fleet' | 'campaigns' | 'hitl';

function TabButton(props: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={props.onClick}
      className={[
        'inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 focus-visible:ring-offset-2',
        props.active ? 'bg-slate-900 text-white' : 'bg-white text-slate-700 hover:bg-slate-50',
        'border border-slate-200',
      ].join(' ')}
      type="button"
    >
      {props.children}
    </button>
  );
}

export function OrchestratorDashboard() {
  const [tab, setTab] = useState<TabKey>('fleet');

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50">
      <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-10">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
                Orchestrator Dashboard
              </h1>
              <Badge variant="outline" className="bg-white">
                SRS UI 1.0 / UI 1.1
              </Badge>
            </div>
            <p className="mt-2 text-sm text-slate-600">
              Mission Control for fleet health, campaign planning, and HITL review.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <TabButton active={tab === 'fleet'} onClick={() => setTab('fleet')}>
              Fleet
            </TabButton>
            <TabButton active={tab === 'campaigns'} onClick={() => setTab('campaigns')}>
              Campaigns
            </TabButton>
            <TabButton active={tab === 'hitl'} onClick={() => setTab('hitl')}>
              HITL
            </TabButton>
          </div>
        </header>

        <section className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">Fleet</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">4</div>
              <div className="mt-1 text-xs text-slate-500">Demo agents online</div>
            </CardContent>
          </Card>
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">HITL queue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">9</div>
              <div className="mt-1 text-xs text-slate-500">Pending human review</div>
            </CardContent>
          </Card>
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">Spend guardrails</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">$50</div>
              <div className="mt-1 text-xs text-slate-500">Max daily spend (USDC)</div>
            </CardContent>
          </Card>
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">Actions</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <Button size="sm" variant="outline">
                Pause fleet
              </Button>
              <Button size="sm">
                New campaign
              </Button>
            </CardContent>
          </Card>
        </section>

        <main className="mt-6">
          {tab === 'fleet' ? (
            <FleetStatusView />
          ) : tab === 'campaigns' ? (
            <CampaignComposer />
          ) : (
            <div className="-mx-4 sm:mx-0">
              {/* Reuse HITL dashboard view */}
              <HitlDashboard />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default OrchestratorDashboard;

