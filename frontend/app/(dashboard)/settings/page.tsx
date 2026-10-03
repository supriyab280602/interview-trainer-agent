'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function Settings() {
  return (
    <div className="max-w-xl mx-auto space-y-8 text-left">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">System Settings</h1>
        <p className="text-sm text-text-secondary">Configure platform options and service credentials.</p>
      </div>

      <Card className="p-6 space-y-6">
        <div className="space-y-4">
          <h3 className="font-semibold text-text-primary text-base">Model Preferences</h3>
          <div className="p-4 bg-surface-secondary border border-border-custom rounded-xl text-sm">
            <span className="text-text-muted block text-xs">Active Engine</span>
            <span className="font-semibold text-text-primary mt-1 block">IBM Granite-3-8b-instruct</span>
          </div>
        </div>

        <Button variant="primary" className="w-full">
          Save Settings
        </Button>
      </Card>
    </div>
  );
}
