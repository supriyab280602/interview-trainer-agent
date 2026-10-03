'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function Profile() {
  const [name, setName] = React.useState('Supriya B.');
  const [role, setRole] = React.useState('Software Engineer');
  const [exp, setExp] = React.useState('1-3 Years');

  return (
    <div className="max-w-xl mx-auto space-y-8 text-left">
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">Profile Configuration</h1>
        <p className="text-sm text-text-secondary">Manage your active career profile and interview customization parameters.</p>
      </div>

      <Card className="p-6 space-y-6">
        <Input label="Full Name" value={name} onChange={(e) => setName(e.target.value)} />
        <Input label="Target Professional Role" value={role} onChange={(e) => setRole(e.target.value)} />
        <Input label="Experience Level" value={exp} onChange={(e) => setExp(e.target.value)} />
        
        <Button variant="primary" className="w-full">
          Save Profile Updates
        </Button>
      </Card>
    </div>
  );
}
